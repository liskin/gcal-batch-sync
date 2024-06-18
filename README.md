# gcal-sync 🚧👷🚧

[![PyPI Python Version badge](https://img.shields.io/pypi/pyversions/gcal-sync)](https://pypi.org/project/gcal-sync/)
[![PyPI Version badge](https://img.shields.io/pypi/v/gcal-sync)](https://pypi.org/project/gcal-sync/)
![License badge](https://img.shields.io/github/license/liskin/gcal-sync)

## Overview

gcal-sync is a … 🚧👷🚧

<!-- FIXME: example image -->

## Installation

Using [pipx][]:

```
pipx ensurepath
pipx install gcal-sync
```

To keep a local git clone around:

```
git clone https://github.com/liskin/gcal-sync
make -C gcal-sync pipx
```

Alternatively, if you don't need the isolated virtualenv that [pipx][]
provides, feel free to just:

```
pip install gcal-sync
```

[pipx]: https://github.com/pypa/pipx

## Usage

<!-- include tests/readme/help.md -->
    $ gcal-sync --help
    Usage: gcal-sync [OPTIONS]
    
      TODO
    
    Options:
      -v, --verbose  Logging verbosity (0 = WARNING, 1 = INFO, 2 = DEBUG)
      --help         Show this message and exit.
<!-- end include tests/readme/help.md -->

<!-- FIXME: example -->

## Contributing

### Code

We welcome bug fixes, (reasonable) new features, documentation improvements,
and more. Submit these as GitHub pull requests. Use GitHub issues to report
bugs and discuss non-trivial code improvements; alternatively, get in touch
via [IRC/Matrix/Fediverse](https://work.lisk.in/contact/).

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details about the code base
(including running tests locally).

Note that this project was born out of a desire to solve a problem I was
facing. While I'm excited to share it with the world, keep in mind that I'll
be prioritizing features and bug fixes that align with my personal use cases.
There may be times when I'm busy with other commitments and replies to
contributions might be delayed, or even occasionally missed. Progress may come
in bursts. Adjust your expectations accordingly.

### Donations (♥ = €)

If you like this tool and wish to support its development and maintenance,
please consider [a small donation](https://www.paypal.me/lisknisi/10EUR) or
[recurrent support through GitHub Sponsors](https://github.com/sponsors/liskin).

By donating, you'll also support the development of my other projects. You
might like these:

* [strava-ical](https://github.com/liskin/strava-ical) – Generate iCalendar with your Strava activities
* [foursquare-swarm-ical](https://github.com/liskin/foursquare-swarm-ical) – Sync Foursquare Swarm check-ins to local sqlite DB and generate iCalendar
