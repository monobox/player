## Gstreamer

### Porting to 1.0

* https://wiki.ubuntu.com/Novacut/GStreamer1.0
* https://github.com/rubenrua/GstreamerCodeSnippets/tree/master/1.0/Python/pygst-tutorial

### Debugging

* http://gstreamer.freedesktop.org/data/doc/gstreamer/head/gstreamer/html/gst-running.html


## Sample streaming sources

* PLS: http://somafm.com/groovesalad.pls
* Stream: http://uwstream1.somafm.com:80

Simplest invocation:

```
$ gst-launch-1.0 playbin uri=http://uwstream1.somafm.com:80
```

## Main api entry point

* http://api.monobox.net/stations
