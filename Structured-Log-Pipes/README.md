# Small Preface

I had initially written a small blurb about how I was allowing AI to write the first half of this article - 
a measure I could take to ensure you - the reader - had the appropriate knowledge and understanding of the
why, what, how, of the UNIX Philosophy.

I expressed in my little prompt my opinion for why it breaks down for large projects,
and why the UNIX philosophy isn't a tool we can appropriately apply to software write large (even small and medium software frankly)

And I even went as far as to fence the AI text from the rest - explaining what you could skip, and what was not my own.

I don't think care enough about informing you of any context you might be missing anymore -
it really serves _no_ purpose to have AI write anything for me. You can have AI write the same for yourself.

I no longer feel a need or responsibility to be a great writer - 
I no longer feel a need to provide my peers with the perfect conceptual framework of my understanding of a topic before I offer them a rant or ramble.

Now more than ever - it's kind of on you to explore and find that information, whether you use AI to help is a personal choice.

So I've removed the AI text from this article - it's in git if you care, though I don't see why you would.

# The UNIX Philosophy

> This is the Unix philosophy: 
> Write programs that do one thing and do it well. 
> Write programs to work together. 
> Write programs to handle text streams, because that is a universal interface.
> - Doug McIlroy (2003). The Art of Unix Programming: Basics of the Unix Philosophy

The UNIX Philosophy is one of those things... It's clean, appealing, and hard to argue against.

I rarely see 'good' software with the UNIX Philosophy applied.

Do we care that `ls` in coreutils [is over 4000 LoC](https://github.com/wertarbyte/coreutils/blob/master/src/ls.c) ?

No, no honestly I could care less.

I don't mean to be indifferent,
it's just that whatever effect the UNIX Philosophy had on me has faded over the years.

A few contenders have come into the scene since then -
namely PowerShell and nushell -
which aim to prove the principals of the philosophy by introducing structured text as the interface between functions and scripts.

As much as I hate using PowerShell, they got that one right.

However I still have issues using these shells because I can't always predict the shape and schema of data before it gets passed around.
Or worse, I'm dealing with a system which is so flaky that I can't ever trust a simple script to build me a list of remote resources before it's network craps out again.

A lot of my frustrations, and the unique environment I've been working in for the past 5 years has continued to push me down a path of Effectual Event Sourcing.

So - this is a simple example of what exactly I mean by that.

Instead of relying on the _output_ of a script to match the correct schema for a different script - 
Let's try and get a little more explicit about what our data and systems are trying to do.

Within any system, there are _Events_ and _Reactions to those Events_.
In this example, we will preform a bit of effectual work, and emit an event in the form of a structured log.
This structured log can be saved to file, or it can be piped into other scripts for them to react to those events.

If a task is genuinely too complex to be captured by one of these events - that's fine.
We can bridge our past practices like building Sqlite Databases, dumping NPY binaries, or orchestrating services on remote hosts the same as we ever have...
Only now, we can log the _fact_ of the effect and rely on the _fact_ to mean something.
Save a giant NPY binary? Great - just log where you put the file, and now any downstream process you create can find and retrieve it. 
> This again is a problem people _still_ haven't quite figured out when building fully scaled applications so who knows if this is actually helpful.

The goal here isn't to create a perfect Event Sourcing application - rather, just express _what we could be doing_ with Structured Logging and the UNIX Philosophy.


# Sprint 1 - Goals

- JSONL stdout for structured event emission
- Type-safe event parsing (Python dataclasses)
- Composable via UNIX pipes

## Features: Piping structured data in and out of `fibwait.py`

I made `fibwait.py` to illustrate the concept - roughed out but works.

```bash
without-objective/Structured-Log-Pipes$ ./fibwait.py 
# {"a": 1, "b": 2}

without-objective/Structured-Log-Pipes$ ./fibwait.py | ./fibwait.py 
# {"a": 2, "b": 3}

without-objective/Structured-Log-Pipes$ ./fibwait.py | ./fibwait.py | ./fibwait.py
# {"a": 3, "b": 5}
```

The main idea here would be to do all sorts of complex Side-Effect driving work, and then wrap that work in Structured Logging _as we should anyway_.
Then, this can be used to control scripts down the line - or simply produce a log of work completed.

## Problems with...

> P: JSONL does look ugly though, it would be nice to have a Logging Format that is slightly more human readable that works for this.

`logfmt` is _an_ alternative - I wont say better but it does at least have good support and colored formatting.

> P: The stdin parsing system inside fibwait sucks though, we can't really expect people to write this themselves.

> P: fibwait is a bad example.

> P: Since I'm introducing libraries in scripts - are we just going to expect users to make a venv compatible with new libraries I need??

## New Requirements (Needs)

> N: Need at a utility file to capture the complexities we are introducing to make this easy to use - otherwise it's too much effort

> N: Let's make a simple Content Addressable Storage example instead of fibwait

A very nice feature I hadn't thought about until now -
because we are relying on logging, we can write to stdout _and_ file pretty easily.

> N: If we are writing to logfiles, how do we handle parallel processes?

> F: Slapping a PID to the filename has been good enough so far -
> treating 'logs' as a collection also helps. _Expect_ that querying is the interface

# A Better Example - File Scanning

> at this point my organization broke down. oh well

## Effectual Scripting: Partition Scanning

Firstly, I just learned that [UV allows dependencies to be declared in situ](https://docs.astral.sh/uv/guides/scripts/#declaring-script-dependencies)
and this is easily the coolest and most needed technologies ever.

Let's make a simple `ls` replacement using structured logging:

```bash
chmod +x scan_partition.py
uv add --script scan_partition.py pandas
```

```python
#!/usr/bin/env -S uv run --script

# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "logfmter",
#     "pandas",
#     "rich",
# ]
# ///

import os
from pathlib import Path
from slap import setup_logging, log_kw

setup_logging()

root_directory = Path("~/Pictures/").expanduser().as_posix()

for root, _, files in os.walk(root_directory):
    for file in files:
        file_path = os.path.join(root, file)
        log_kw("File Discovered", entry=file_path, root=root_directory)
```

The script is simple - and mostly relies on outsourcing our logging to the `slap` file - which handles saving to file as well now.

This allows us to make a _very_ rudimentary event sourcing log.

Obviously - these can't be used _quite_ like an event sourcing database.
We can re-run this script over and over again - only to find it reproducing events that exist in older files.
Events in this log are not idempotent - and this is fine.

We're looking for something easy after all - but consider what this gives us:

When we build a more complex ETL pipeline, we are automatically saving a context of work accomplished. If we get smart about querying this data, we can automate some of the control plane without having to define additional files and filetypes.

Let's continue this pipeline to see what I mean (because I don't know the answer yet either).

I have copied all of the photos off of my phone and put them on this laptop to scan. I want to upload them to a Content Addressable Storage, and collect some information about what I have so that I can make predictions about future work.

My Operating System and File System knows what files exist - but I don't.
To solve for this, we introduced a simple `ls` replacement. 
This scans our files and dumps what we learn into a myriad of logfiles.

We want to use these logfiles to schedule new work - so first let's think about the work we want to do:

1. How much data do I have? Based on file sizes, is there anything surprising?
2. How many unique file types are there? I know I have a lot of images and some video. What about PDF's and DOCX?
3. How many duplicate files do I have? Hopefully not many - but we can hash our data and find out.
4. 'Uploading' the data is likely going to be error prone - simply because I'm on a laptop, the process will be long, and I might forget to plug my laptop back in while it processes. Before you comment to suggest I do something else - imagine being a company running a similar process at scale when boom - Cloudflare, AWS, or Starlink go down. Can you're software handle the inevitable failures of the infrastructure surrounding it?

To start - let's acquire some initial info. I ran the `scan_partition.py` script twice and killed it early both times to ensure I had some duplicate events in my `logs/` folder - and that everything is working. 
I'll commit those logs - idk about the rest yet.

We'll make a new tiny script called `stat_partition.py` and set it up similarly.
We'll also add some magic to `slap.py` so that we can read in these logs and deduplicate them for reading.

```python
#!/usr/bin/env -S uv run --script

# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "logfmter",
#     "logfmt",
#     "pandas",
#     "rich",
# ]
# ///

import os
from pathlib import Path
from slap import read_logs, setup_logging, log_kw
from datetime import datetime

setup_logging()

log_snapshot = read_logs()

print(len(log_snapshot['File Discovered']))

for discovery in log_snapshot['File Discovered']:
    file_path = discovery['entry']
    root = discovery['root']

    # one way to pro-actively guard against duplicating work
    if 'File Stat Collected' in log_snapshot:
        already_collected = any(stat['entry'] == file_path for stat in log_snapshot['File Stat Collected'])
        if already_collected:
            continue

    try:
        stat_info = os.stat(file_path)

        file_size = stat_info.st_size
        modified_time = datetime.fromtimestamp(stat_info.st_mtime).isoformat()
        created_time = datetime.fromtimestamp(stat_info.st_ctime).isoformat()
        file_ext = Path(file_path).suffix.lower()

        log_kw(
            "File Stat Collected",
            entry=file_path,
            root=root,
            size_bytes=file_size,
            extension=file_ext,
            modified=modified_time,
            created=created_time,
        )
    except (OSError, PermissionError) as e:
        log_kw("File Stat Error", entry=file_path, error=str(e))
```

The cool bit here is that we can query our logs to determine if we want to re-do work again or not.

After re-mangling the `slap.py` file we can support piping again - which get's us a full scan and stat system.

Since we are obviously still building our pipeline, we can rely on our saved logs to pipe directly into the future components as well.

To test this out, we'll create a `hash_items.py` script and `cat` an older log into it.

`cat logs/114174_20251206_112355_scan_partition.log | ./hash_items.py`


```
./analyze_data.py 

═══ File System Analysis ═══

╭─────── Overview ──────────────────────────────╮
│ Files Discovered: 11457                       │
│ Files Stat'd: 11457                           │
│ Files Hashed: 11457                           │
╰───────────────────────────────────────────────╯
╭── File Size Statistics ──╮
│ Total Size: 27.36 GB     │
│ Min Size: 0.00 B         │
│ Max Size: 747.73 MB      │
│ Avg Size: 2.45 MB        │
╰──────────────────────────╯
           File Type Distribution            
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┓
┃ Extension            ┃ Count ┃ Percentage ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━┩
│ .jpg                 │  9173 │      80.1% │
│ .png                 │  1343 │      11.7% │
│ .mp4                 │   484 │       4.2% │
│ .dng                 │   184 │       1.6% │
│ .pdf                 │    93 │       0.8% │
│ True                 │    28 │       0.2% │
│ .jpeg                │    28 │       0.2% │
│ .m4a                 │    26 │       0.2% │
│ .txt                 │    12 │       0.1% │
│ .heic                │    11 │       0.1% │
│ .epub                │    10 │       0.1% │
│ .apk                 │    10 │       0.1% │
│ .md                  │     9 │       0.1% │
│ .ogg                 │     8 │       0.1% │
│ .json                │     6 │       0.1% │
└──────────────────────┴───────┴────────────┘
... and 15 more extension types

╭────── Duplicate Analysis ───────────────────╮
│ Unique Duplicate Content: 115               │
│ Total Duplicate Files: 293                  │
│ Extra Copies: 178                           │
│ Wasted Space: 76.80 MB                      │
╰─────────────────────────────────────────────╯
                   Top Duplicated Files                   
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Hash (first 16)    ┃ Copies ┃ Size Each ┃ Total Wasted ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ 20b4ef66dda6f204   │     11 │  39.82 KB │    398.21 KB │
│ 080b2ec50ee57da5   │     11 │  48.28 KB │    482.81 KB │
│ 786a02f742015903   │      7 │    0.00 B │       0.00 B │
│ 6253e8502ba8217b   │      5 │ 522.07 KB │      2.04 MB │
│ 7abc4f7bfab7bb0c   │      5 │ 380.27 KB │      1.49 MB │
│ 430493f5b07d416b   │      5 │  79.53 KB │    318.14 KB │
│ dc15f27fcc77f8ee   │      5 │ 410.99 KB │      1.61 MB │
│ c27dba9016682923   │      5 │  90.54 KB │    362.16 KB │
│ 55fe95e6d04a45fa   │      5 │ 971.39 KB │      3.79 MB │
│ a7306fca39dd9265   │      5 │ 433.78 KB │      1.69 MB │
└────────────────────┴────────┴───────────┴──────────────┘
```

---

There's really nothing all that special here, and that's what's so exciting about the approach.
With a bit more polish and some LLM tooling, this can easily replace a few more complicated ETL systems I've developed in the past.

Granted - this is primarily for `Novel` and `Viable` software - not anything more. 
Though, because we are effectively using this to drive an event-based reaction system, 
we can easily use these logs to rebuild Database state (similar to Xpressfeed or other commercial database transfer tools.)

---

Further reading ?

https://pages.cs.wisc.edu/~remzi/Naur.pdf
https://www.arthropod.software/p/vibe-coding-our-way-to-disaster