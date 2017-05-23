# Ubunolia

Ubunolia is a temporally-confused IRC simulator.

## Requirements

Beyond stdlib, you'll need [Urwid](http://urwid.org) and [Algoliasearch](https://www.algolia.com/doc/api-client/python/getting-started/).

## Usage

```
$ python ./ubunolia.py
```

```
Type [help|?] command_name to get more help.                                                             
Type [quit|q] to quit.                                                                                   
Available commands: connect list seen whois
```

Type `connect` to begin the simulation. This will start querying the Algolia
backend and replaying the IRC logs as it it were today.

## What even is time?

Ubunolia is a mashup of both Realist and Leibbniz/Kant time philosophy.
It mashes up *your* time with the past, replaying it as if it were *now*,
except that it *isn't*, so the past can be interpreted as both a sequence of
events and as an intellectual construct in and of itself, concurrently.

## Known Bugs

Yes.
