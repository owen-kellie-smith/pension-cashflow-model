def test_copy_all_output_to_log(tmp_path, capsys):
    from helpers import copy_all_output_to_log

    log_file = tmp_path / "test.log"

    copy_all_output_to_log(log_file)

    print("hello log")

    captured = capsys.readouterr()

    # terminal output still appears
    assert "hello log" in captured.out

    # file output also written
    with open(log_file) as f:
        contents = f.read()

    assert "hello log" in contents
