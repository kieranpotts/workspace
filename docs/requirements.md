# Requirements

[Git LFS](https://git-lfs.com/) SHOULD be installed before cloning the repositories. This is required to download PDFs and other large files from some repositories. But the `git clone` operation will succeed without it.

Python 3 is REQUIRED to run the management scripts.

It is RECOMMENDED to install the [pre-commit](https://pre-commit.com) framework to enable local validation hooks before committing. You need only to run the following command once to install pre-commit system-wide:

```bash
pipx install pre-commit
```

Then install the pre-commit hooks in every local repository where you want pre-commit checks to be run:

```bash
pre-commit install
```

This installs all hook types declared in `.pre-commit-config.yaml` (`pre-commit`, `commit-msg`).

Edit `./.pre-commit-config.yaml` to configure the pre-commit validation checks you want for your project. See the [pre-commit documentation](https://pre-commit.com) for details.


> [!TIP]
> Clone and run the environment [bootstrapping script](https://github.com/kieranpotts/bootstrap) first. This will install Git LFS and other dependencies.
