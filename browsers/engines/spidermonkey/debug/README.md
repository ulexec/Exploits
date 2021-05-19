# A docker debug environment for SpiderMonkey

This repo builds a debug environment to develop and test exploits for SpiderMonkey. It defines a docker image based on Debian with all the dependencies needed to build and run a JavaScript shell. SpiderMonkey's source code should be dropped next to this repo's Docker file. Mozilla use Mercurial to do this but I prefer git:

`git clone --depth 1 https://github.com/mozilla/gecko-dev.git`

A custom patch file is provided to simulate the blazefox CTF challenge (https://ctftime.org/task/6000) that works with the commit where gecko-dev.git's HEAD used to point to when this repo was created. See **blazeCustom.patch** for more.

## GDB support

This image's GDB comes installed by with a copy of GEF (https://gef.readthedocs.io/en/master/). A few extra tools and references are provided to start poking SpiderMonkey's memory for objects and functions:

- Mozilla's own pretty printers are enabled by default (https://blog.mozilla.org/javascript/2013/01/03/support-for-debugging-spidermonkey-with-gdb-now-landed/)
- The file **customFunctions.py** provides custom commands to inspect arrays and JS::Value objects. The jsinfo command takes _tagged pointers, raw pointers or GDB expressions_ - example output follows:

```
js> Math.atan(new Function())

gef➤  jsinfo vp[2]
[*] Parsing JS::Value at     0x7ffff5c350b0
[*] Tagged pointer is        0xfffe0fe7e8bb6040
[*] Tag is                   object
[*] Payload is               0xfe7e8bb6040
[*] Class name is            Function

[*] JSClassOps:
$471 = {
  addProperty = 0x0, 
  delProperty = 0x0, 
  enumerate = 0x555555e62e70 <fun_enumerate(JSContext*, JS::Handle<JSObject*>)>, 
  newEnumerate = 0x0, 
  resolve = 0x555555e631b0 <fun_resolve(JSContext*, JS::Handle<JSObject*>, JS::Handle<JS::PropertyKey>, bool*)>, 
  mayResolve = 0x555555e636d0 <fun_mayResolve(JSAtomState const&, JS::PropertyKey, JSObject*)>, 
  finalize = 0x0, 
  call = 0x0, 
  hasInstance = 0x0, 
  construct = 0x0, 
  trace = 0x555555e637e0 <fun_trace(JSTracer*, JSObject*)>
}
$JS::Value(0xfe7e8bb6040)

js> Math.atan([1,2])

gef➤  jsinfo vp[2]
[*] Parsing JS::Value at     0x7ffff5c350b0
[*] Tagged pointer is        0xfffe0fe7e8b9d0c0
[*] Tag is                   object
[*] Payload is               0xfe7e8b9d0c0
[*] Class name is            Array
[*] Length:                  2

Elements:
0xfe7e8b9d0f0:	0xfff8800000000001	0xfff8800000000002

[*] JSClassOps:
$473 = {
  addProperty = 0x555555c0bdb0 <array_addProperty(JSContext*, JS::Handle<JSObject*>, JS::Handle<JS::PropertyKey>, JS::Handle<JS::Value>)>, 
  delProperty = 0x0, 
  enumerate = 0x0, 
  newEnumerate = 0x0, 
  resolve = 0x0, 
  mayResolve = 0x0, 
  finalize = 0x0, 
  call = 0x0, 
  hasInstance = 0x0, 
  construct = 0x0, 
  trace = 0x0
}
```

## Floating points and IEEE-754

A handful of useful references to get your head around NaN-boxing, etc.

- https://anniecherkaev.com/the-secret-life-of-nan
- http://sandbox.mc.edu/~bennet/cs110/flt/ftod.html
- saelo's int64 library, which I took from https://github.com/saelo/cve-2018-4233

Big integers are now supported in all major browsers and replacing int64.js is left as an exercise for the reader.

## Generational garbage collection

The terms Nursery and Tenured objects will pop up from time to time - this refers to Generational Garbage Collection

- https://hacks.mozilla.org/2014/09/generational-garbage-collection-in-firefox/


## JSAPI and Mozilla

- https://searchfox.org/
- https://gitlab.gnome.org/GNOME/gjs/blob/master/doc/Understanding-SpiderMonkey-code.md
- https://github.com/mozilla/gecko-dev

## Exploitation

- http://www.ouah.org/ELF-runtime-fixup.txt
- https://github.com/saelo/feuerfuchs/blob/master/exploit/pwn.js
- https://grehack.fr/data/2017/slides/GreHack17_Get_the_Spidermonkey_off_your_back.pdf
- https://doar-e.github.io/blog/2018/11/19/introduction-to-spidermonkey-exploitation/#jsvalues-and-jsobjects
