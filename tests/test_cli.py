from click.testing import CliRunner

from cs3560cli.main import cli


def test_top_level_command() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli)
        assert result.exit_code == 0


def test_highlight_command() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli, args=["highlight", "-"], input='print("Hello World")\n'
        )
        assert result.exit_code == 0
        assert not result.exception
        assert result.output.startswith("<div")
        assert "Hello" in result.output


def test_highlight_command_input_via_file() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("main.cpp", "w") as f:
            f.write("""#include <iostream>
int main() {
    std::cout << "Hello World!" << std::endl;
}""")

        result = runner.invoke(cli, args=["highlight", "./main.cpp", "-o", "-"])
        assert result.exit_code == 0
        assert not result.exception
        assert result.output.startswith("<div")
        assert "cout" in result.output
        assert "Hello" in result.output
