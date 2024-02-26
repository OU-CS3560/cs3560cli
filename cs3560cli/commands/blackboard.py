"""
The blackboard sub comamnd.
"""

import json
import socket
import sys
import time
import webbrowser
from multiprocessing import Process
from pathlib import Path

import click
from flask import Flask, render_template, request

from cs3560cli.blackboard import categorize, filter_by_role, parse_url_for_course_id

template_dir_path = Path(__file__).parent.parent / "templates"
static_dir_path = Path(__file__).parent.parent / "static"
STUDENT_LIST_URL = "https://blackboard.ohio.edu/learn/api/public/v1/courses/{course_id}/users?fields=id,userId,user,courseRoleId"


def create_app():
    """Create simple flask application for a web UI."""
    app = Flask(
        __name__, template_folder=template_dir_path, static_folder=static_dir_path
    )

    @app.route("/", methods=["GET", "POST"])
    def show_index():
        if request.method == "GET":
            return render_template("index.html")
        elif request.method == "POST":
            return ""

    @app.route("/get-link", methods=["POST"])
    def get_link():
        course_url = request.form.get("courseUrl", "")
        course_id = parse_url_for_course_id(course_url)
        link = STUDENT_LIST_URL.format(course_id=course_id)
        return f"""
<div id="target" class="collapse bg-base-200">
    <input type="radio" name="my-accordion-1" checked="checked" /> 
    <div class="collapse-title text-xl font-medium">
        Visit this link and copy back the JSON data.
    </div>
    <div class="collapse-content">
        <form hx-post="/submit-data" hx-target="#target" hx-swap="outerHTML">
            <div>
                <a href="{link}" target="_blank">{link}</a>
            </div>
            <div>
                <textarea name="jsonData" wrap="off" class="textarea my-4" style="width: 600px;" placeholder="Paste the JSON data from the link above here"></textarea>
            </div>
            <div>
                <button class="btn">Submit</button>
            </div>
        </form>
    </div>
</div>
"""

    @app.route("/submit-data", methods=["POST"])
    def submit_data():
        raw_data = request.form.get("jsonData", "")
        data = json.loads(raw_data)
        students = filter_by_role(data["results"])

        payload = "firstName\tlastName\temailHandle\tisDrop\tgithub-username\tteam-id\tteam-name\tm1\tm2\tm3\tm4\tfinal\tassigned-ta\tnote\tdiscord-username\tcodewars-username\tuserId\tcourseMembershipId\n"
        row_template = "{first_name}\t{last_name}\t{email_handle}\t{is_drop}\t{github_username}\t{team_id}\t{team_name}\t{m1}\t{m2}\t{m3}\t{m4}\t{final}\t{assigned_ta}\t{note}\t{discord_username}\t{codewars_username}\t{user_id}\t{course_membership_id}\n"
        for entry in students:
            payload += row_template.format(
                first_name=entry["user"]["name"]["given"],
                last_name=entry["user"]["name"]["family"],
                email_handle=entry["user"]["userName"],
                is_drop="N",
                github_username="",
                team_id="",
                team_name="",
                m1="",
                m2="",
                m3="",
                m4="",
                final="",
                assigned_ta="",
                note="",
                discord_username="",
                codewars_username="",
                user_id=entry["userId"],
                course_membership_id=entry["id"],
            )
        return f"""
<div class="collapse bg-base-200">
    <input type="radio" name="my-accordion-1" checked="checked" /> 
    <div class="collapse-title text-xl font-medium">
        Result
    </div>
    <div class="collapse-content">
        <div>
            You can copy this TSV to a new Excel file or <a href="https://sheets.new/" target="_blank">Google Sheet</a>
        </div>
        <div>
            <textarea rows="30" wrap="off" class="textarea my-4" style="width: 600px;">{payload}</textarea>
        </div>
    </div>
</div>"""

    return app


def run_web_server(port):
    app = create_app()
    app.run(port=port, debug=False)


@click.group()
def blackboard():
    """Blackboard related tools."""
    pass


@blackboard.command(name="student-list")
@click.argument("course_url", nargs=1, required=False)
def student_list_command(course_url):
    """Obtain a list of student form Blackboard's API."""
    if course_url is None:
        """Show/open web UI."""

        # Acquire a random port.
        # See https://stackoverflow.com/a/5089963/10163723
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("localhost", 0))
        port = sock.getsockname()[1]
        sock.close()

        server = Process(target=run_web_server, args=(port,))
        server.start()

        url = f"http://localhost:{port}/"
        try:
            webbrowser.open(url)
        except:
            click.echo(
                f"Cannot open a browser to '{url}', please manually open the URL in your browser."
            )

        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            # signal will not work on Windows?
            click.echo("Terminating the internal web server ...")
            server.terminate()
            server.join()
    else:
        course_id = parse_url_for_course_id(course_url)
        if course_id is None:
            print(f"[error]: Cannot parse '{course_url}' for course ID.")
            click.exit(1)

        print(
            f"\nStudent list link:\n\n{STUDENT_LIST_URL.format(course_id=course_id)}\n\nVisit the link above in your browser."
        )
        print(
            "Then copy and paste in the JSON data below and hit Ctrl-D (EOF) when you are done:\n"
        )

        data = sys.stdin.read()
        results = json.loads(data)
        students = filter_by_role(results["results"])

        print("TSV data of the students:\n\n")
        print(
            "firstName\tlastName\temailHandle\tisDrop\tgithub-username\tteam-id\tteam-name\tm1\tm2\tm3\tm4\tfinal\tassigned-ta\tnote\tdiscord-username\tcodewars-username\tuserId\tcourseMembershipId"
        )
        row_template = "{first_name}\t{last_name}\t{email_handle}\t{is_drop}\t{github_username}\t{team_id}\t{team_name}\t{m1}\t{m2}\t{m3}\t{m4}\t{final}\t{assigned_ta}\t{note}\t{discord_username}\t{codewars_username}\t{user_id}\t{course_membership_id}"
        for entry in students:
            row = row_template.format(
                first_name=entry["user"]["name"]["given"],
                last_name=entry["user"]["name"]["family"],
                email_handle=entry["user"]["userName"],
                is_drop="N",
                github_username="",
                team_id="",
                team_name="",
                m1="",
                m2="",
                m3="",
                m4="",
                final="",
                assigned_ta="",
                note="",
                discord_username="",
                codewars_username="",
                user_id=entry["userId"],
                course_membership_id=entry["id"],
            )
            print(row)


@blackboard.command(name="categorize")
@click.argument(
    "source",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=True, readable=True, writable=True
    ),
    required=True,
)
@click.argument(
    "destination",
    type=click.Path(
        exists=False, file_okay=False, dir_okay=True, readable=True, writable=True
    ),
    required=True,
)
def categorize_command(source, destination):
    """Group files from the same student together in a folder."""
    click.echo("Categorizing files ...")
    categorize(source, destination)
