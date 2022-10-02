
# IRC bot

A simple IRC bot that can connect to an IRC server via TCP-IP (IPv6 by default) and responds to private and channel messages, providing useful functionality to its users.


[![issues](https://img.shields.io/github/issues/kaiuerlichs/irc_bot)](https://github.com/kaiuerlichs/irc_bot/issues)
[![prs](https://img.shields.io/github/issues-pr/kaiuerlichs/irc_bot)](https://github.com/kaiuerlichs/irc_bot/pulls)
## Authors

- [@jlyons](https://www.github.com/jlyons)
- [@heathercurrie](https://github.com/heathercurrie)
- [@ross-coombs](https://github.com/ross-coombs)
- [@kaiuerlichs](https://github.com/kaiuerlichs)


## Usage

To run the bot, clone the directory and run the following command:
```bash
  python bot.py 
```
Add `--help` for help using the command-line options, which will allow you to set hostname, port number, the bot nickname and the channel to monitor.

## Run Locally with miniircd

Clone the project as well as miniircd as your server
```bash
  git clone https://github.com/kaiuerlichs/irc_bot.git
  git clone https://github.com/jrosdahl/miniircd.git
```

Start miniircd
```bash
  cd miniircd
  python miniircd --ipv6 --debug
```

Start bot
```bash
  cd ../irc_bot
  python bot.py --host ::1
```
