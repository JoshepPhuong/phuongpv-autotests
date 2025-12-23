# Selenium plugin

This is a plugin for `pytest` that provides webdriver for tests. It allows to run tests in
chrome, firefox and edge browsers and also supports remote browser.

There are bunch of added options to manage webdriver:

* `--webdriver` - Specify a browser to run tests against (`chrome` (default), `firefox`, `edge`, `remote`).
* `--webdriver-remote` to run browser remotely.
* `--webdriver-headless` - Run browser in headless mode"
* `--webdriver-window-size` - Size of browser window in pixels"
* `--webdriver-implicitly-wait` - An implicit wait tells WebDriver to poll the DOM for a certain
  amount of time when trying to find any element (or elements) not immediately available in seconds,
  has to be lower than global wait parameter
* `--webdriver-remote-url` - Url to remote drivers hub

To get a webdriver in tests just use `webdriver_getter` fixture:

```python
@pytest.fixture(scope="session")
def webdriver(
    request: SubRequest,
    webdriver_getter,
) -> WebDriver:
    """Initialize webdriver for unauthorized session."""
    return webdriver_getter(request)
```

## Why not pytest-splinter or pytest-selenium?

`pytest-selenium `is a good plugin, but it's missing a key feature we need - `session`(`module`) scope browser
session and according to `github` [issue](https://github.com/pytest-dev/pytest-selenium/issues/59) they are not going
to add this any time soon. It also still [doesn't support `pytest>=7.0.0`](https://github.com/pytest-dev/pytest-selenium/issues/305).

Why not `pytest-splinter` then? Well it has a session scoped browser session and even a
factory, it's limited by three browsers (`firefox`, `chrome` and `remote`) and we're using only it's factory fixtures.
Since we wanted to support the safari browser, we wrote our own custom plugin. Now that we gave up support for safari,
we checked if we could replace the custom plugin with `pytest-splinter`. We decided that there was no point in using
`pytest-splinter` on the current project because:

* `pytest-splinter` is not really actively maintained
* We already have plugin that works well for our autotests structure
* It needs to override bunch of fixtures and configurations for `pytest-splinter`
  to replace our implementation. So it's kind of like replacing one bunch of code
  with another.

## Why no safari support?

After spending a lot of time investigating it was decided to not support it. Mostly because
`safaridriver` works completely different the `chromedriver` or `geckodriver`. Some feature doesn't work
completely like actionChains or a simple click. We were trying safari 13 and 14.

Here a list of issues we encountered:

* `Waits` doesn't work completely on safari 13, it fails with `500` error with a message - `unknown error`.
  [Link](https://developer.apple.com/forums/thread/118493)

* On safari 14 the only way to click on something is by executing `js script`, nothing else works
  [Link](https://developer.apple.com/forums/thread/658705)

* `ActionsChains` doesn't completely, event a simple click.
  [Link](https://developer.apple.com/forums/thread/662677)

* `safaridriver` return response after commands almost instantly compared to others when they wait for a page to
  start loading. It breaks many tests, for example changing password: after completing form, we submitting it and driver
  waits a little and then continues to execute next commands, but `safaridriver` instantly goes to log in a page, while
  form wasn't submitted as all, thus user still has an old password. It can be solved by overriding execute method in
  `SafariWebDriver`, but it slows tests down way too much.

* Sometimes a `NoSuchFrameException` popups on `waits` or `find_elements`, even thought the
  entire app doesn't use `iframes` or selenium methods related to it at all. After investigating,
  it theorized that it happens when there is no object that matches `locator`.

* For some reason when typing into fields it can fail with Exception, the only fix
  is in `fill` method of `Element` class - don't reuse element and instead call self._get_element
  every time.

* Safari 14 doesn't work with remote selenium hubs, in our case it's `selenoid`.
  [Link](https://github.com/aerokube/selenoid/issues/1070#issuecomment-793071729)

And this only a tip of iceberg, because we failed to fix all tests and after checking that
percent of safari usage is about `3%`, we decided to drop it.
