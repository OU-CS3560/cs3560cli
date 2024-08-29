from cs3560cli.lms.canvas import parse_url_for_course_id


def test_parse_url_for_course_id():
    assert (
        parse_url_for_course_id("https://ohio.instructure.com/courses/24840") == "24840"
    )
    assert (
        parse_url_for_course_id(
            "https://ohio.instructure.com/courses/24840/pages/content-overview?module_item_id=500553"
        )
        == "24840"
    )
    assert (
        parse_url_for_course_id(
            "https://ohio.instructure.com/calendar#view_name=month&view_start=2024-08-29"
        )
        is None
    )
