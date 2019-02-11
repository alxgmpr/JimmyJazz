# JimmyJazz Bot

An auto-checkout script to purchase shoes from JimmyJazz. Uses a 'sock-jig' type of method to preload checkout with
a dummy item. Then at release time the dummy item is removed and the real item is checked out.

# Requirements

* py3
* requests
* termcolor

# Installation

Clone down from repository, `cd` into it, then run `pip3 install -r requirements.txt`.

# Configuration

Change `config.json`, `proxies.txt` and `tasks.json` as necessary.

Retry delay is the time (in seconds) to wait before retrying a request. 5XX errors will retry the request, otherwise
the program will die on 4XX errors. JimmyJazz's website can and will go down during releases. These retries have not
been tested on a release yet. Please give me a log of your request data if you receive errors or the program behaves
erratically.

Please note that drop time (in `config.json`) is 24 hour format of the local timezone on the machine. `MM/DD/YY HH:MM:SS`.

Proxies should be formatted like `[IP]:[PORT]:[USER]:[PASS]` or `[IP]:[PORT]` to use IP authorization instead of basic auth.

To make multiple tasks, add more objects to the `tasks.json` file like so:

```json
{
  "tasks": [
    { ...task 1... },
    { ...task 2... },
    { ...task n... }
  ]
}
```

Where each task can represent a different billing and different target variant.

Card type can be either `Visa` or `MasterCard`. Maybe Amex but I haven't tested that since I dont own one.

USA address only. Use the postal abbreviation for your state.

The proxy manager uses a 'wrap-around' method of distributing proxies. If there are more tasks than proxies, proxies
will be reused for subsequent tasks. Proxy use can be disabled for individual tasks in `tasks.json` objects, which will
ignore the wrap-around

# Running

`python3 main.py`

If something goes wrong, `ctrl + C` like crazy.

Variants can usually be found around the day before the drop. :)

A good strategy is to use Privacy burner cards on multiple tasks of the same size, so the billing profile will only be
used once.


Copyright 2019 Alexander Gompper.