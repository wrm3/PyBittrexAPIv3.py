# loc_bittrex_v3.py
This project works with the new Bittrex REST API 3.0.

Bittrex announced that it was retiring the Bittrex API 1.1 in September 2020 (3 months), and encouraged us to switch to the new 3.0 API.  I had been using a modified version of ericsomdahl's python-bittrex.  My own personal private project (trading bot) which requires this library is going to need a significant overall, and this was just the first step to get that project going...  I really am only putting this out there for someone to help get the new GET/HEAD/POST/DELETE with payload concepts figure out.  It was a struggle, and what I found online was definitely not helpful.

With the following issues: the "get conditional orders" appears to want the trade symbols reversed to the old order (ie USD-BTC) vs the new Forex style (BTC-USD).  I think its a problem on Bittrex end.  In addition the old python-bittrex calls are now multiple calls to the new API, so there is no direct correlation so far as Market Summary and Currencies...

I probably should be doing this as a branch of eric somdahls' project, but it doesn't do what his did because of all of the changes, this is just a stepping stone to get my personal project working on the new 3.0 API.  I also don't have time to figure out how to use github to properly, this is all fairly rushed.  I apologize for not posting this in the correct 'git' way, but from my own fruitless searching I could tell that others are probably in the same boat as me and decided to get it out there.  If there wasn't a rampant virus, family health emergencies, and a full time job to deal with, I would have taken the time to do this right. Good Luck. I hope to come back someday and develop this all properly.

I like Bitcoin!
Donate BTC: 1NoxcCMCdQoBtC5dprBHxfZDSk1VPWpWFV
