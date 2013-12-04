/* The MIT License (MIT)
 * 
 * Copyright (c) 2013 Michael Bikovitsky
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

(function(){

var array = null;
var messagesLoaded = false;
var current_index = 0;
var video_delay = 0;

var chat_sim = null;

var paused = true;
var messageTimer = null, videoTimer = null;

// Adapted from http://stackoverflow.com/a/3969760/851560
function Timer(callback, delay) {
    var timerId, start, remaining = delay;

    var ticking = false;    // Indicates whether timer is active (not paused)
    var finished = false;   // Indicates whether timer already "fired"
    var callbackWrapper = function () {
        finished = true;
        ticking = false;
        callback();
    };

    this.pause = function () {
        if (!finished) {
            if (!ticking) { return; }   // Do nothing if timer already paused
            window.clearTimeout(timerId);
            remaining -= new Date() - start;
            ticking = false;
        }
    };

    this.resume = function () {
        if (!finished) {
            if (ticking) { return; }    // Do nothing if timer already active
            start = new Date();
            timerId = window.setTimeout(callbackWrapper, remaining);
            ticking = true;
        }
    };

    this.isFinished = function () {
        return finished;
    };

    this.resume();
    ticking = true;
}

var print_message = function () {
    chat_sim.append("<p>" + array[current_index].message + "</p>");
    chat_sim.animate({ scrollTop: chat_sim[0].scrollHeight }, "slow");
    current_index++;
    if (current_index < array.length) {
        messageTimer = new Timer(print_message, array[current_index].delay);
    }
};

var playVideo = function () {
    // This is the first time playing
    if (!videoTimer) {
        videoTimer = new Timer(playVideo, video_delay);
        return;
    }

    // Resume video timer (does nothing if timer already "fired")
    videoTimer.resume();

    // If timer already "fired" (video began playing on cue),
    // resume player
    if (videoTimer.isFinished()) {
        $("#live_embed_player_flash")[0].playVideo();
    }
};

var pauseVideo = function () {
    // Pause video timer (to ensure it doesn't begin playing)
    videoTimer.pause();

    // Pause player in case it's already playing
    $("#live_embed_player_flash")[0].pauseVideo();
};

var playMessages = function () {
    // This is the first time playing
    if (!messageTimer) {
        print_message();
        return;
    }
    
    messageTimer.resume();
};

var pauseMessages = function () {
    messageTimer.pause();
};

// Click event handler
var click_play = function (e) {
    if (messagesLoaded && window.playerLoaded) {
        if (paused) {
            playMessages();
            playVideo();
            paused = false;
        } else {
            pauseMessages();
            pauseVideo();
            paused = true;
        }
    }
    
    e.preventDefault();
    return false;
};

// Get filename
var filename = window.location.pathname.split('/');
filename = filename[filename.length - 1];
filename = filename.split('.')[0] + ".json";

// Load messages
$.getJSON(filename, function(data) {
    video_delay = data[0];
    array = data[1];
    messagesLoaded = true;
});

$(document).ready(function() {
    $("#play_all").click(click_play).removeClass("hidden");
    $.getScript("data/timer.js", function () {
        $("#wideChat").removeClass("hidden");
    });
    chat_sim = $("#chat_sim");
});

})();
