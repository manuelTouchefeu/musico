"use strict";

// player
// Specify globally used values
var playList = document.querySelector("#playlist");
var track_list = []
var track_index = 0;
var isPlaying = false;
var fileIsLoaded = false;
var fileIsLoadedOnServer = false;
var next_btn = document.querySelector(".next-track");
var prev_btn = document.querySelector(".prev-track");
var track_name = document.querySelector("#track-name");
var track_artist = document.querySelector("#track-artist");
var stop_btn = document.querySelector(".stop");
var playPause_btn = document.querySelector(".playpause-track");
var volume_slider = document.querySelector(".volume_slider");
var seek_slider = document.querySelector(".seek_slider");
var clearPlaylist = document.querySelector("#clearPlaylist");
var equalizer = document.querySelector("#equalizer");

var total_duration = document.querySelector(".total-duration");
var curr_time = document.querySelector(".current-time");

// Create the audio element for the player
var curr_track = document.createElement('audio');
var curr_track_path = "";
var curr_track_duration = 0;

// Load the playlist, add the eventListeners
Array.from(document.querySelectorAll(".playListItem")).forEach(function(elt) {
    elt.addEventListener("click", function(e) {
        let playListIndex = e.target.querySelector("input[name='track_index']").value;
        loadTrack(playListIndex);
        track_index = parseInt(playListIndex);
    }, false)
});

(function() {
    let xhr = new XMLHttpRequest();
    let host = window.location.origin + "/get_track_list";
    xhr.open('POST', host);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    xhr.send(JSON.stringify({"message": "track_list"}));
    // Réception des données.
    xhr.addEventListener('readystatechange', function() {
        if (xhr.readyState === xhr.DONE) {
            let response = xhr.responseText
            track_list = JSON.parse(xhr.responseText);

        }
    }, false);
})();


// set output
var outButton = document.querySelector("#out");
var local = outButton.innerText == "Local" ? true : false;

outButton.addEventListener("click", function(e) {
    local = !local //(local == true ? false : true);
    outButton.innerText = (local == true ? "Local" : "Serveur");
    //clearPlayer()
    // init the player if server
    // get the server state.
    if (!local) {
        let xhr = new XMLHttpRequest();
        // Envoi de la requête.
        let host = window.location.origin + "/server_info";
        xhr.open('POST', host);
        xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        xhr.send(JSON.stringify({question: "question"}));
        // Réception des données.
        xhr.addEventListener('readystatechange', function() {
            if (xhr.readyState === xhr.DONE) {
                let response = JSON.parse(xhr.responseText);
                console.log(response);
                if (response['state'] == "PLAY") {
                    isPlaying = true;
                    track_name.textContent = response['title'];
                    track_artist.textContent = response['artist'];
                    playPause_btn.querySelector("img").src="/static/images/pause.png";
                    equalizer.src = "/static/images/icons8-audio-wave.gif/";
                    // Set an interval of 1000 millisecond for updating the seek slider
                    updateTimer = setInterval(seekUpdate, 1000);
                    // Init the volume button
                }
            }
        }, false);
    }
    //return response;
}, false);


// add to the playlist
function savePlaylist() {
    let xhr = new XMLHttpRequest();
     // new ajax request -> save the playlist
    let host = window.location.origin + "/save_playlist"
    xhr.open('POST', host);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    xhr.send(JSON.stringify({playlist: track_list}));
    xhr.addEventListener('readystatechange', function() {
        if (xhr.readyState === xhr.DONE) {
            let response = xhr.responseText
            // nothing is done
        }
    }, false);
}

// album
function addToPlaylist(e) {
    // get the full album
    let xhr = new XMLHttpRequest();
    // Envoi de la requête.
    let host = window.location.origin + '/get_album'
    xhr.open('POST', host);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    xhr.send(JSON.stringify({album_id: e.target.value}));
    // Réception des données.
    xhr.addEventListener('readystatechange', function() {
        if (xhr.readyState === xhr.DONE) {
            let response = xhr.responseText
            let json = JSON.parse(xhr.responseText);
            json.forEach(function(e) {
                let newPlayListItem = document.createElement("p");
                newPlayListItem.setAttribute("class", "playListItem");
                newPlayListItem.classList.add("not-played");
                newPlayListItem.innerText = e.track_number + " - " + e.track_title;
                let track_index_input = document.createElement("input");
                track_index_input.type = "hidden";
                track_index_input.name = "track_index";
                track_index_input.value = track_list.length;
                newPlayListItem.appendChild(track_index_input);
                track_list.push(e);
                let playListIndex = track_list.length - 1;
                playList.appendChild(newPlayListItem);

                newPlayListItem.addEventListener("click", function(npi) {
                    loadTrack(playListIndex);
                    track_index = playListIndex
                }, false);
            });
            savePlaylist();
        }
    }, false);
}


// tracks
function addTrackToPlayList(e) {
    let track_id = e.target.value;
    let xhr = new XMLHttpRequest();
    // Envoi de la requête.
    let host = window.location.origin + '/get_track'
    xhr.open('POST', host);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    xhr.send(JSON.stringify({track_id: track_id}));
    // Réception des données.
    xhr.addEventListener('readystatechange', function() {
        if (xhr.readyState === xhr.DONE) {
            let response = xhr.responseText
            let json = JSON.parse(xhr.responseText);
            let newPlayListItem = document.createElement("p");
            newPlayListItem.setAttribute("class", "playListItem");
            newPlayListItem.classList.add("not-played");
            newPlayListItem.innerText = json.track_number + " - " + json.track_title;
            let track_index_input = document.createElement("input");
            track_index_input.type = "hidden";
            track_index_input.name = "track_index";
            track_index_input.value = track_list.length;
            newPlayListItem.appendChild(track_index_input);
            track_list.push(json);
            let playListIndex = track_list.length - 1;
            playList.appendChild(newPlayListItem);

            newPlayListItem.addEventListener("click", function(npi) {
                loadTrack(playListIndex);
                track_index = playListIndex
            }, false);
            savePlaylist();
        }
    }, false);
}

function addEvents() {
    let addTrackToPlaylistButtons = document.querySelectorAll('.addTrackToPlaylist');
    Array.from(addTrackToPlaylistButtons).forEach(function(b) {
        b.addEventListener('click', addTrackToPlayList, false);
    });
    let addToPlaylistButtons = document.querySelectorAll('.addToPlaylist');
    Array.from(addToPlaylistButtons).forEach(function(b) {
        b.addEventListener('click', addToPlaylist, false);
    });
}

// clear the playlist
clearPlaylist.addEventListener("click", function(e) {
    let xhr = new XMLHttpRequest();
    // Envoi de la requête.
    let host = window.location.origin + "/clear_playlist";
    xhr.open('POST', host);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    xhr.send(JSON.stringify({album_id: e.target.value}));
    // Réception des données.
    xhr.addEventListener('readystatechange', function() {
        if (xhr.readyState === xhr.DONE) {    console.log("playTrack", fileIsLoadedOnServer);

            let response = xhr.responseText
            Array.from(document.querySelectorAll(".playListItem")).forEach(function(elt) {
                elt.remove();
            } );
            track_list = [];
        }
    }, false)
}, false);


// sent command to server
function sentCommandToServer(instruction, arg=null) {
    let xhr = new XMLHttpRequest();
    // Envoi de la requête.    console.log("playTrack", fileIsLoadedOnServer);

    let host = window.location.origin + "/play";
    xhr.open('POST', host);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    xhr.send(JSON.stringify({instruction: instruction, arg: arg}));
    // Réception des données.
    xhr.addEventListener('readystatechange', function() {
        if (xhr.readyState === xhr.DONE) {
            let response = xhr.responseText;
            console.log(response);
        }
    }, false);
}


// player
var updateTimer = null;
function loadTrack(track_index) {
    // Clear the previous seek timer
    clearInterval(updateTimer);
    resetValues();
     // Load a new track
    track_name.textContent = track_list[track_index].track_title;
    track_artist.textContent = track_list[track_index].artist_name;

    curr_track.src = "/" + track_list[track_index].path;
    curr_track_path = track_list[track_index].path;
    curr_track.load();
    fileIsLoaded = true;
    playTrack();

    document.querySelectorAll(".playListItem").forEach(function(elt) {
        if (elt.querySelector("input[name='track_index']").value == track_index) {
            elt.classList.replace("not-played", "played");
        }
        else {
            elt.classList.replace("played", "not-played");
        }
    });
    // Set an interval of 1000 millisecond for updating the seek slider
    updateTimer = setInterval(seekUpdate, 1000);
    // Move to the next track if the current finishes playing using the 'ended' event
    if (local) { curr_track.addEventListener("ended", nextTrack); }
    // the same operation in seekUpdate for the server side
}

function playPause() {
    if (!fileIsLoaded && track_list.length > 0) {
        loadTrack(0);
        document.querySelector(".playListItem").classList.replace("not-played", "played");
    }
    else if (!isPlaying) {
        playTrack();
    }
    else {
        pauseTrack();
    }
}
playPause_btn.addEventListener("click", playPause, false);

function playTrack() {
    // Play the loaded track
    if (local == true) {
        curr_track.play();
    }
    else if (fileIsLoadedOnServer == false) {
        sentCommandToServer("playit", curr_track_path);
        fileIsLoadedOnServer = true;
    }
    else { // server, file loaded on server is different of the current one ? ask it!
        let xhr = new XMLHttpRequest();
        // Envoi de la requête.
        let host = window.location.origin + "/server_info";
        xhr.open('POST', host);
        xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        xhr.send(JSON.stringify({instruction: "instruction"}));
        // Réception des données.
        xhr.addEventListener('readystatechange', function() {
            if (xhr.readyState === xhr.DONE) {
                let response = JSON.parse(xhr.responseText);
                // new file
                if (response["file"].indexOf(curr_track_path) == -1) {
                    sentCommandToServer("playit", curr_track_path);
                }
                else {
                    sentCommandToServer("play");
                }
            }
        }, false);
    }
    isPlaying = true;
    // Replace icon with the pause icon
    playPause_btn.querySelector("img").src="/static/images/pause.png";
    equalizer.src = "/static/images/icons8-audio-wave.gif/";
}

function pauseTrack() {
  // Pause the loaded track
  if (local == true) {
        curr_track.pause();
    }
    else {
        sentCommandToServer("pause")
    }
  isPlaying = false;
  // Replace icon with the play icon
  playPause_btn.querySelector("img").src="/static/images/play.png";
  equalizer.src = "/static/images/icons8-audio-wave-50.png/";
}


// add to listened album
function addListenedAlbum(albumId) {
    let xhr = new XMLHttpRequest();
    let host = window.location.origin + "/add_listened_album"
    xhr.open('POST', host);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    xhr.send(JSON.stringify({albumId: albumId}));
    xhr.addEventListener('readystatechange', function() {
        if (xhr.readyState === xhr.DONE) {
            let response = xhr.responseText
            // nothing is done
        }
    }, false);
}

function nextTrack() {
    if (local == false) {
        fileIsLoadedOnServer = false;
    }
    if (track_index < track_list.length - 1 && fileIsLoaded) {
        // add album to last listened albums
        console.log(track_list[track_index].album_id);
        if (track_list[track_index].album_id == track_list[track_index + 1].album_id) { // two tracks on tof the same album
            addListenedAlbum(track_list[track_index].album_id)
        }
        console.log(track_list);


        track_index += 1;
        // Load and play the new track
        loadTrack(track_index);
    }
    else {
         // Go back to the first track if the current one is the last in the track list
        track_index = 0;
        clearPlayer();
    }
}
next_btn.addEventListener("click", nextTrack, false);

function prevTrack() {
    // Go back to the last track if the current one is the first in the track list
    if (track_index > 0) {
        track_index -= 1;
    }
    if (local == false) {
        fileIsLoadedOnServer = false;
    }    // Load and play the new track
    loadTrack(track_index);
}
prev_btn.addEventListener("click", prevTrack, false);



function clearPlayer() {
    fileIsLoaded = false;
    fileIsLoadedOnServer = false;
    Array.from(document.querySelectorAll(".playListItem")).forEach(function(e) {
        e.classList.replace("played", "not-played");
    } );
    //curr_track.clear();
    curr_track.src = "";
    curr_track.removeAttribute("src");
    track_name.textContent = "";
    track_artist.textContent = "";
    playPause_btn.querySelector("img").src="/static/images/play.png";
    equalizer.src = "/static/images/icons8-audio-wave-50.png/";
    track_index = 0;
    resetValues();
    if (local == false) {
        sentCommandToServer("stop");
        fileIsLoadedOnServer = false;
    }
    isPlaying = false;
    clearInterval(updateTimer);
}

function resetValues() {
    curr_time.textContent = "00:00";
    total_duration.textContent = "00:00";
    seek_slider.value = 0;
    curr_track_path = "";
    curr_track_duration = 0
}

stop_btn.addEventListener("click", function() {
    clearPlayer();
}, false);


function setVolume() {
    // Set the volume according to the percentage of the volume slider set
    if (local == true) {
        curr_track.volume = volume_slider.value / 100;
    }
    else {
        sentCommandToServer("volume", volume_slider.value)
    }
}
volume_slider.addEventListener("change", setVolume, false);




function seekTo() {
    if (local) {
        // Calculate the seek position by the percentage of the seek slider and get the relative duration to the track
        curr_track.currentTime = curr_track.duration * (seek_slider.value / 100);
        // Set the current track position to the calculated seek position
    }
    else {
        sentCommandToServer("seek", Math.floor(curr_track_duration * (seek_slider.value / 100)));
    }
}
seek_slider.addEventListener("change", seekTo, false);


function seekUpdate() {
    let seekPosition = 0;
    let currentMinutes = 0;
    let currentSeconds = 0;
    let durationMinutes = 0;
    let durationSeconds = 0;

    if (local) {
        // Check if the current track duration is a legible number
        if (!isNaN(curr_track.duration)) {
            seekPosition = curr_track.currentTime * (100 / curr_track.duration);
            seek_slider.value = seekPosition;
            //Calculate the time left and the total duration
            currentMinutes = Math.floor(curr_track.currentTime / 60);
            currentSeconds = Math.floor(curr_track.currentTime - currentMinutes * 60);
            durationMinutes = Math.floor(curr_track.duration / 60);
            durationSeconds = Math.floor(curr_track.duration - durationMinutes * 60);
            // Add a zero to the single digit time values
            if (currentSeconds < 10) { currentSeconds = "0" + currentSeconds; }
            if (durationSeconds < 10) { durationSeconds = "0" + durationSeconds; }
            if (currentMinutes < 10) { currentMinutes = "0" + currentMinutes; }
            if (durationMinutes < 10) { durationMinutes = "0" + durationMinutes; }

            // Display the updated duration
            curr_time.textContent = currentMinutes + ":" + currentSeconds;
            total_duration.textContent = durationMinutes + ":" + durationSeconds;
        }
    }
    else { // server
        let xhr = new XMLHttpRequest();
        // Envoi de la requête.
        let host = window.location.origin + "/server_info";
        xhr.open('POST', host);
        xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        xhr.send(JSON.stringify({question: "question"}));
        // Réception des données.
        xhr.addEventListener('readystatechange', function() {
            if (xhr.readyState === xhr.DONE) {
                let response = JSON.parse(xhr.responseText);
                if (response["state"] == "STOP") {
                    if (isPlaying) { nextTrack(); }
                    return;
                }
                let currentTime = parseInt(response["currentSeconds"]);
                curr_track_duration = parseInt(response["duration"]);
                if (!isNaN(currentTime) && !isNaN(curr_track_duration)) {
                    seekPosition = currentTime * (100 / curr_track_duration);
                    seek_slider.value = seekPosition;
                    //Calculate the time left and the total duration
                    currentMinutes = Math.floor(currentTime / 60);
                    currentSeconds = Math.floor(currentTime - currentMinutes * 60);
                    durationMinutes = Math.floor(curr_track_duration / 60);
                    durationSeconds = Math.floor(curr_track_duration - durationMinutes * 60);
                    // Add a zero to the single digit time values
                    if (currentSeconds < 10) { currentSeconds = "0" + currentSeconds; }
                    if (durationSeconds < 10) { durationSeconds = "0" + durationSeconds; }
                    if (currentMinutes < 10) { currentMinutes = "0" + currentMinutes; }
                    if (durationMinutes < 10) { durationMinutes = "0" + durationMinutes; }

                    // Display the updated duration
                    curr_time.textContent = currentMinutes + ":" + currentSeconds;
                    total_duration.textContent = durationMinutes + ":" + durationSeconds;

                    // for clients who join a server already loaded and playing a track
                    // toDo
                }
            }
        }, false);
    }
}
//https://www.geeksforgeeks.org/create-a-music-player-using-javascript/


// navigation
var content = document.querySelector("#content");

var linkGenres = document.querySelector("#link_genres");
var linkAlbums = document.querySelector("#link_albums");
var linkArtists = document.querySelector("#link_artists");


function goToAlbums() {
    let xhr = new XMLHttpRequest();
    // Envoi de la requête.
    let host = window.location.origin + '/albums/';
    xhr.open('POST', host);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    xhr.send(JSON.stringify({hello: "hello"}));
    // Réception des données.
    xhr.addEventListener('readystatechange', function() {
        if (xhr.readyState === xhr.DONE) {
            let response = xhr.responseText
            content.innerHTML = response;
            // add eventListeners
            goToAlbum();
            goToArtist();
            addEvents();
        }
    }, false);
}
linkAlbums.addEventListener("click", goToAlbums, false);
// init the first page
goToAlbums();


function goToAlbum() {
    let linkAlbum = document.querySelectorAll(".link_album");
    Array.from(linkAlbum).forEach(function(l) {
        l.addEventListener("click", function(e) {
            let albumId = e.target.parentNode.querySelector(".target").value;
            let xhr = new XMLHttpRequest();
            // Envoi de la requête.
            let host = window.location.origin + '/album/';
            xhr.open('POST', host);
            xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
            xhr.send(JSON.stringify({album_id: albumId}));
            // Réception des données.
            xhr.addEventListener('readystatechange', function() {
                if (xhr.readyState === xhr.DONE) {
                    let response = xhr.responseText
                    content.innerHTML = response;
                    // add eventListeners
                    goToArtist();
                    addEvents();
                    goToGenre();
                }
            }, false);
        }, false);
    })
}

function goToArtists() {
    let xhr = new XMLHttpRequest();
    // Envoi de la requête.
    let host = window.location.origin + '/artists/';
    xhr.open('POST', host);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    xhr.send(JSON.stringify({hello: "hello"}));
    // Réception des données.
    xhr.addEventListener('readystatechange', function() {
        if (xhr.readyState === xhr.DONE) {
            let response = xhr.responseText
            content.innerHTML = response;
            // add eventListeners
            goToArtist();
            addEvents();
        }
    }, false);
}
linkArtists.addEventListener("click", goToArtists, false);

function goToArtist() {
    let linkArtist = document.querySelectorAll(".link_artist");
    Array.from(linkArtist).forEach(function(l) {
        l.addEventListener("click", function(e) {
            let artistId = e.target.parentNode.querySelector(".target").value;
            let xhr = new XMLHttpRequest();
            // Envoi de la requête.
            let host = window.location.origin + '/artist/';
            xhr.open('POST', host);
            xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
            xhr.send(JSON.stringify({artist_id: artistId}));
            // Réception des données.
            xhr.addEventListener('readystatechange', function() {
                if (xhr.readyState === xhr.DONE) {
                    let response = xhr.responseText
                    content.innerHTML = response;
                    goToAlbum();
                    addEvents();
                }
            }, false);
        }, false);
    })
}

function goToGenres() {
    let xhr = new XMLHttpRequest();
    // Envoi de la requête.
    let host = window.location.origin + '/genres/';
    xhr.open('POST', host);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    xhr.send(JSON.stringify({hello: "hello"}));
    // Réception des données.
    xhr.addEventListener('readystatechange', function() {
        if (xhr.readyState === xhr.DONE) {
            let response = xhr.responseText
            content.innerHTML = response;
            // add eventListeners
            goToGenre();
            addEvents();
        }
    }, false);
}
linkGenres.addEventListener("click", goToGenres, false);

function goToGenre() {
    let linkGenre = document.querySelectorAll(".link_genre");
    Array.from(linkGenre).forEach(function(l) {
        l.addEventListener("click", function(e) {
            let genreId = e.target.parentNode.querySelector(".target").value;
            let xhr = new XMLHttpRequest();
            // Envoi de la requête.
            let host = window.location.origin + '/genre/';
            xhr.open('POST', host);
            xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
            xhr.send(JSON.stringify({genre_id: genreId}));
            // Réception des données.
            xhr.addEventListener('readystatechange', function() {
                if (xhr.readyState === xhr.DONE) {
                    let response = xhr.responseText
                    content.innerHTML = response;
                    goToAlbum();
                    addEvents();
                }
            }, false);
        }, false);
    })
}


// search
var searchButton = document.querySelector("#searchButton");
var searchInput = document.querySelector("#search");


function search() {
    let pattern = searchInput.value;
    let xhr = new XMLHttpRequest();
    // Envoi de la requête.
    let host = window.location.origin + '/search';
    xhr.open('POST', host);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    xhr.send(JSON.stringify({pattern: pattern}));
    // Réception des données.
    xhr.addEventListener('readystatechange', function() {
        if (xhr.readyState === xhr.DONE) {
            let response = xhr.responseText
            content.innerHTML = response;
            // add eventListeners
            goToAlbum();
            goToArtist();
            goToGenre();
        }
    }, false);
}
searchButton.addEventListener("click", search, false);


// update database
document.querySelector("#update_db").addEventListener("click", function(e) {
    let xhr = new XMLHttpRequest();
    // Envoi de la requête.
    let host = window.location.origin + "/update_db/";
    xhr.open('POST', host);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    xhr.send(JSON.stringify({order: "update_db"}));
    // Réception des données.
    xhr.addEventListener('readystatechange', function() {
        if (xhr.readyState === xhr.DONE) {
            let response = xhr.responseText
            console.log(response)
        }
    }, false);

}, false);


// keyboard events
window.addEventListener("keydown", (event) => {
    switch (event.code) {
        case "Enter":
            event.preventDefault();
            search();
            break;
        case "Space":
            // except if the focus is on search field
            if (document.activeElement != searchInput) {
                event.preventDefault();
                playPause();
            }
            break;
    }
});
