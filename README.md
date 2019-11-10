# Tekinbot

Tekinbot is a simple and expandable discord bot who runs on Python, discord.py, love, and Discord API, and who could serve great utility to your Discord server!

## Preparation:

0.  You need python3.6+, together with MySQL and SQLite

1.  First of all, set up a python [virtual environment](https://docs.python.org/3/tutorial/venv.html) by running `make venv`

2.  Run `make install-hooks` to install pre-commit hooks

3.  `git checkout -b <your-branch-name>`, and hack away!
    For this repo, I recommend using a meaningful branch name, and recommend using the format
    `git checkout -b <github_username-issue_number-branch_name>`

4.  Run `make dev` to make a local server instance so you could test your changes,
    note that the `make dev` instance runs with `--dry-run` and `--no-db` options, meaning that:

    you could also run (in venv) `python3 -m tekinbot.tekin` with any options,
    run with `-h` or `--help` to see the available dev options.

5.  After making your changes, `git push origin <your-branch-name>`,
    for this repo, let me know that your branch is ready to be merged

6.  If you have a discord server to test it on:
    *   get your tekin's discord tokens and put them in a `tekin-secrets` config;
        by default, this config is in `~/.tekin-secrets.yaml`, you need to have a section in that config like
        ```{yaml}
        discord:
            bot_token: yourbottokenhere
        ```
        You will also need some database configs in this secrets file, see the [Database section below](https://github.com/nanflasted/TekinBot#how-to-tekin-database).

        For an example of this `tekin-secrets` config, see [here](https://github.com/nanflasted/TekinBot/tree/master/config/dev/.tekin-secrets.yaml).
    *   You can then see your tekinbot addition in live action! EHHHHHHH!

7.  You've dunnit! Remember what Tekin would say: take a 5 minute break, drink some water and wash your face...

## How to add a new module:

1.  All current modules can be seen in [this directory](https://github.com/nanflasted/TekinBot/tree/master/tekinbot/comms),
    if you would like some examples to look at.

2.  Modules are usually implemented as `discord.py`'s `Cog`s. Check [their document](https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#cogs) for more.

3.  Add your module to the [comms/\_\_init\_\_.py](https://github.com/nanflasted/TekinBot/blob/master/tekinbot/comms/__init__.py),
    and its individual submodule's \_\_init\_\_.py

#### things we all know we should do but we won't do:

4.  After implementing writing both of these functions and any other additional requirements that a module might have, you
    should then write unit tests for your comms module.

5.  Commit your changes, fix any things that may be caught by the pre-commit hooks, then `make test`; if any of the test fails,
    fix accordingly.

## How to Tekin database:

0.  First of all, you will need `mysql-server` running on your dev if you want to do any manual testing at all. See [here](https://help.ubuntu.com/lts/serverguide/mysql.html) to see how to set it up on Ubuntu environments. This project uses SqlAlchemy ORM to deal with all the database transactions; for a quick tutorial see [here](http://docs.sqlalchemy.org/en/latest/orm/tutorial.html)

    You will also need to `CREATE` a database named `tekinbot` in MySQL.

    If you do not want to give Tekinbot `root` access to mysql-server, make a user and configure it in `tekin-secrets` config (see above), and make sure to `GRANT` proper priviledges to the user you created; minimally, CRUD-related priviledges should be given.

1.  Figure out what kind of tables you will need, and make a table model similar to [this one](https://github.com/nanflasted/TekinBot/blob/master/tekinbot/db/models/karma.py) in the same directory (tekinbot/db/models); after you   are done writing your table schemas, add your table to [the db module](https://github.com/nanflasted/TekinBot/blob/master/tekinbot/db/models/__init__.py)

2.  Implement your module; tekin uses a singleton as SqlAlchemy `engine`, and with that engine creates a single `SessionMaker`, to get these instances, use the utilities from [`tekinbot.utils.db`](https://github.com/nanflasted/TekinBot/blob/master/tekinbot/utils/db.py)

3.  To test on your machine, supply your MySQL-server's access credentials in the `.tekin-secrets.yaml` file, by default it is located at `~/.tekin-secrets.yaml`, you can change the yaml file to be at a different location, but don't commit it as part of your change; make sure the yaml file a dictionary similar to this:
    ```{yaml}
    database:
        username: <your-tekin-user-name>
        password: hunter2
    ```

4.  When you `make dev`, all the tables in the directory tekinbot/db/models will be initiated if they don't exist yet. Run python, import your module, and test away! Though, **do** note that `make dev` defaults to use an in-memory sqlite database; to use actual MySQL database, run `python3 -m tekinbot.tekin` **without** the `--no-db` option.

5.  For NS's instance of Tekin, if after a feature has been shipped, you need a table model changed, figure out the correct `ALTER TABLE` command, and include it in your pull request.
