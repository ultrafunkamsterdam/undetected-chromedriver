(function (name, context, definition) {
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = definition();
    } else if (typeof define === 'function' && define.amd) {
        define(definition);
    } else {
        context[name] = definition();
    }
})('Fingerprint', this, function () {
    'use strict';

    var Fingerprint = function (options) {
        var nativeForEach, nativeMap;
        nativeForEach = Array.prototype.forEach;
        nativeMap = Array.prototype.map;

        this.each = function (obj, iterator, context) {
            if (obj === null) {
                return;
            }
            if (nativeForEach && obj.forEach === nativeForEach) {
                obj.forEach(iterator, context);
            } else if (obj.length === +obj.length) {
                for (var i = 0, l = obj.length; i < l; i++) {
                    if (iterator.call(context, obj[i], i, obj) === {}) return;
                }
            } else {
                for (var key in obj) {
                    if (obj.hasOwnProperty(key)) {
                        if (iterator.call(context, obj[key], key, obj) === {}) return;
                    }
                }
            }
        };

        this.map = function (obj, iterator, context) {
            var results = [];
            // Not using strict equality so that this acts as a
            // shortcut to checking for `null` and `undefined`.
            if (obj == null) return results;
            if (nativeMap && obj.map === nativeMap) return obj.map(iterator, context);
            this.each(obj, function (value, index, list) {
                results[results.length] = iterator.call(context, value, index, list);
            });
            return results;
        };

        if (typeof options == 'object') {
            this.hasher = options.hasher;
            this.screen_resolution = options.screen_resolution;
            this.screen_orientation = options.screen_orientation;
            this.canvas = options.canvas;
            this.ie_activex = options.ie_activex;
        } else if (typeof options == 'function') {
            this.hasher = options;
        }
    };

    Fingerprint.prototype = {
        get: function () {
            var keys = [];
            keys.push(navigator.userAgent);
            keys.push(navigator.language);
            keys.push(screen.colorDepth);
            if (this.screen_resolution) {
                var resolution = this.getScreenResolution();
                if (typeof resolution !== 'undefined') { // headless browsers, such as phantomjs
                    keys.push(resolution.join('x'));
                }
            }
            keys.push(new Date().getTimezoneOffset());
            keys.push(this.hasSessionStorage());
            keys.push(this.hasLocalStorage());
            keys.push(this.hasIndexDb());
            //body might not be defined at this point or removed programmatically
            if (document.body) {
                keys.push(typeof (document.body.addBehavior));
            } else {
                keys.push(typeof undefined);
            }
            keys.push(typeof (window.openDatabase));
            keys.push(navigator.cpuClass);
            keys.push(navigator.platform);
            keys.push(navigator.doNotTrack);
            keys.push(this.getPluginsString());
            if (this.canvas && this.isCanvasSupported()) {
                keys.push(this.getCanvasFingerprint());
            }
            if (this.hasher) {
                return this.hasher(keys.join('###'), 31);
            } else {
                return this.murmurhash3_32_gc(keys.join('###'), 31);
            }
        },

        /**
         * JS Implementation of MurmurHash3 (r136) (as of May 20, 2011)
         *
         * @author Gary Court
         * @see http://github.com/garycourt/murmurhash-js
         * @author Austin Appleby
         * @see http://sites.google.com/site/murmurhash/
         *
         * @param {string} key ASCII only
         * @param {number} seed Positive integer only
         * @return {number} 32-bit positive integer hash
         */

        murmurhash3_32_gc: function (key, seed) {
            var remainder, bytes, h1, h1b, c1, c2, k1, i;

            remainder = key.length & 3; // key.length % 4
            bytes = key.length - remainder;
            h1 = seed;
            c1 = 0xcc9e2d51;
            c2 = 0x1b873593;
            i = 0;

            while (i < bytes) {
                k1 =
                    ((key.charCodeAt(i) & 0xff)) |
                    ((key.charCodeAt(++i) & 0xff) << 8) |
                    ((key.charCodeAt(++i) & 0xff) << 16) |
                    ((key.charCodeAt(++i) & 0xff) << 24);
                ++i;

                k1 = ((((k1 & 0xffff) * c1) + ((((k1 >>> 16) * c1) & 0xffff) << 16))) & 0xffffffff;
                k1 = (k1 << 15) | (k1 >>> 17);
                k1 = ((((k1 & 0xffff) * c2) + ((((k1 >>> 16) * c2) & 0xffff) << 16))) & 0xffffffff;

                h1 ^= k1;
                h1 = (h1 << 13) | (h1 >>> 19);
                h1b = ((((h1 & 0xffff) * 5) + ((((h1 >>> 16) * 5) & 0xffff) << 16))) & 0xffffffff;
                h1 = (((h1b & 0xffff) + 0x6b64) + ((((h1b >>> 16) + 0xe654) & 0xffff) << 16));
            }

            k1 = 0;

            switch (remainder) {
                case 3:
                    k1 ^= (key.charCodeAt(i + 2) & 0xff) << 16;
                case 2:
                    k1 ^= (key.charCodeAt(i + 1) & 0xff) << 8;
                case 1:
                    k1 ^= (key.charCodeAt(i) & 0xff);

                    k1 = (((k1 & 0xffff) * c1) + ((((k1 >>> 16) * c1) & 0xffff) << 16)) & 0xffffffff;
                    k1 = (k1 << 15) | (k1 >>> 17);
                    k1 = (((k1 & 0xffff) * c2) + ((((k1 >>> 16) * c2) & 0xffff) << 16)) & 0xffffffff;
                    h1 ^= k1;
            }

            h1 ^= key.length;

            h1 ^= h1 >>> 16;
            h1 = (((h1 & 0xffff) * 0x85ebca6b) + ((((h1 >>> 16) * 0x85ebca6b) & 0xffff) << 16)) & 0xffffffff;
            h1 ^= h1 >>> 13;
            h1 = ((((h1 & 0xffff) * 0xc2b2ae35) + ((((h1 >>> 16) * 0xc2b2ae35) & 0xffff) << 16))) & 0xffffffff;
            h1 ^= h1 >>> 16;

            return h1 >>> 0;
        },

        // https://bugzilla.mozilla.org/show_bug.cgi?id=781447
        hasLocalStorage: function () {
            try {
                return !!window.localStorage;
            } catch (e) {
                return true; // SecurityError when referencing it means it exists
            }
        },

        hasSessionStorage: function () {
            try {
                return !!window.sessionStorage;
            } catch (e) {
                return true; // SecurityError when referencing it means it exists
            }
        },

        hasIndexDb: function () {
            try {
                return !!window.indexedDB;
            } catch (e) {
                return true; // SecurityError when referencing it means it exists
            }
        },

        isCanvasSupported: function () {
            var elem = document.createElement('canvas');
            return !!(elem.getContext && elem.getContext('2d'));
        },

        isIE: function () {
            if (navigator.appName === 'Microsoft Internet Explorer') {
                return true;
            } else if (navigator.appName === 'Netscape' && /Trident/.test(navigator.userAgent)) {// IE 11
                return true;
            }
            return false;
        },

        getPluginsString: function () {
            if (this.isIE() && this.ie_activex) {
                return this.getIEPluginsString();
            } else {
                return this.getRegularPluginsString();
            }
        },

        getRegularPluginsString: function () {
            return this.map(navigator.plugins, function (p) {
                var mimeTypes = this.map(p, function (mt) {
                    return [mt.type, mt.suffixes].join('~');
                }).join(',');
                return [p.name, p.description, mimeTypes].join('::');
            }, this).join(';');
        },

        getIEPluginsString: function () {
            if (window.ActiveXObject) {
                var names = ['ShockwaveFlash.ShockwaveFlash',//flash plugin
                    'AcroPDF.PDF', // Adobe PDF reader 7+
                    'PDF.PdfCtrl', // Adobe PDF reader 6 and earlier, brrr
                    'QuickTime.QuickTime', // QuickTime
                    // 5 versions of real players
                    'rmocx.RealPlayer G2 Control',
                    'rmocx.RealPlayer G2 Control.1',
                    'RealPlayer.RealPlayer(tm) ActiveX Control (32-bit)',
                    'RealVideo.RealVideo(tm) ActiveX Control (32-bit)',
                    'RealPlayer',
                    'SWCtl.SWCtl', // ShockWave player
                    'WMPlayer.OCX', // Windows media player
                    'AgControl.AgControl', // Silverlight
                    'Skype.Detection'];

                // starting to detect plugins in IE
                return this.map(names, function (name) {
                    try {
                        new ActiveXObject(name);
                        return name;
                    } catch (e) {
                        return null;
                    }
                }).join(';');
            } else {
                return ""; // behavior prior version 0.5.0, not breaking backwards compat.
            }
        },

        getScreenResolution: function () {
            var resolution;
            if (this.screen_orientation) {
                resolution = (screen.height > screen.width) ? [screen.height, screen.width] : [screen.width, screen.height];
            } else {
                resolution = [screen.height, screen.width];
            }
            return resolution;
        },

        getCanvasFingerprint: function () {
            var canvas = document.createElement('canvas');
            var ctx = canvas.getContext('2d');
            // https://www.browserleaks.com/canvas#how-does-it-work
            var txt = 'http://valve.github.io';
            ctx.textBaseline = "top";
            ctx.font = "14px 'Arial'";
            ctx.textBaseline = "alphabetic";
            ctx.fillStyle = "#f60";
            ctx.fillRect(125, 1, 62, 20);
            ctx.fillStyle = "#069";
            ctx.fillText(txt, 2, 15);
            ctx.fillStyle = "rgba(102, 204, 0, 0.7)";
            ctx.fillText(txt, 4, 17);
            return canvas.toDataURL();
        }
    };
    return Fingerprint;
});


new Fingerprint({canvas: true}).get();


var inject = function () {
    var overwrite = function (name) {
        const OLD = HTMLCanvasElement.prototype[name];
        Object.defineProperty(HTMLCanvasElement.prototype, name, {
            "value": function () {
                var shift = {
                    'r': Math.floor(Math.random() * 10) - 5,
                    'g': Math.floor(Math.random() * 10) - 5,
                    'b': Math.floor(Math.random() * 10) - 5,
                    'a': Math.floor(Math.random() * 10) - 5
                };
                var width = this.width, height = this.height, context = this.getContext("2d");
                var imageData = context.getImageData(0, 0, width, height);
                for (var i = 0; i < height; i++) {
                    for (var j = 0; j < width; j++) {
                        var n = ((i * (width * 4)) + (j * 4));
                        imageData.data[n + 0] = imageData.data[n + 0] + shift.r;
                        imageData.data[n + 1] = imageData.data[n + 1] + shift.g;
                        imageData.data[n + 2] = imageData.data[n + 2] + shift.b;
                        imageData.data[n + 3] = imageData.data[n + 3] + shift.a;
                    }
                }
                context.putImageData(imageData, 0, 0);
                return OLD.apply(this, arguments);
            }
        });
    };
    overwrite('toBlob');
    overwrite('toDataURL');
};
inject();


new Fingerprint({canvas: true}).get();

