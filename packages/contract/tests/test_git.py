import subprocess

from ygperf.git import capture_git


def test_capture_git_returns_sha_and_dirty_flag(tmp_path):
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "--allow-empty", "-m", "x"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    sha, dirty = capture_git(tmp_path)
    assert len(sha) == 40
    assert not dirty
    (tmp_path / "f.txt").write_text("hi")
    _, dirty2 = capture_git(tmp_path)
    assert dirty2 is True


def test_capture_git_on_non_repo_returns_unknown(tmp_path):
    sha, dirty = capture_git(tmp_path / "nope")
    assert sha == "unknown"
    assert dirty is False
