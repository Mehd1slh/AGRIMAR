document.addEventListener("DOMContentLoaded", function () {
  function loadLottieAnimation(containerId, animationPath) {
    return lottie.loadAnimation({
      container: document.getElementById(containerId),
      renderer: "svg",
      loop: true,
      autoplay: true,
      path: animationPath,
    });
  }

  loadLottieAnimation("about-animation", "static/Animation-About.json");
  loadLottieAnimation("weather-animation", "static/Animation-Weather.json");
  loadLottieAnimation("soil-animation", "static/Animation-Soil.json");
  loadLottieAnimation("ndvi-animation", "static/Animation-NDVI.json");
  loadLottieAnimation("location-animation", "static/Animation-Location.json");

  const blurOverlay = document.getElementById("blur-overlay");
  const mapWindow = document.getElementById("map-window");
  const container = document.querySelector(".container");

  document
    .getElementById("close-map-window")
    .addEventListener("click", function () {
      blurOverlay.style.display = "none";
      container.classList.remove("blur-effect");
      mapWindow.style.display = "none";
    });

  let map, marker;

  function initMap() {
    map = L.map("map").setView([34.007634, -6.838341], 8);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap contributors",
    }).addTo(map);

    map.on("click", function (event) {
      if (marker) map.removeLayer(marker);

      marker = L.marker(event.latlng, { draggable: true }).addTo(map);
      document.getElementById("latitude").value = event.latlng.lat;
      document.getElementById("longitude").value = event.latlng.lng;

      marker.on("dragend", function () {
        const markerLatLng = marker.getLatLng();
        document.getElementById("latitude").value = markerLatLng.lat;
        document.getElementById("longitude").value = markerLatLng.lng;
      });
    });

    document.getElementById("latitude").addEventListener("input", updateMap);
    document.getElementById("longitude").addEventListener("input", updateMap);
  }

  function updateMap() {
    const lat = parseFloat(document.getElementById("latitude").value);
    const lng = parseFloat(document.getElementById("longitude").value);

    if (!isNaN(lat) && !isNaN(lng)) {
      if (marker) map.removeLayer(marker);

      marker = L.marker([lat, lng], { draggable: true }).addTo(map);
      map.setView([lat, lng], 15);

      marker.on("dragend", function () {
        const markerLatLng = marker.getLatLng();
        document.getElementById("latitude").value = markerLatLng.lat;
        document.getElementById("longitude").value = markerLatLng.lng;
      });
    }
  }

  document
    .getElementById("location-btn")
    .addEventListener("click", function () {
      mapWindow.style.display = "block";
      blurOverlay.style.display = "block";
      container.classList.add("blur-effect");
      initMap();
    });

  document
    .getElementById("location-form")
    .addEventListener("submit", function (event) {
      event.preventDefault();
      const lat = document.getElementById("latitude").value;
      const lng = document.getElementById("longitude").value;

      if (lat && lng) {
        blurOverlay.style.display = "none";
        container.classList.remove("blur-effect");
        mapWindow.style.display = "none";
        this.submit();
      } else {
        console.error("Latitude and longitude are required.");
      }
    });

  // Chatbot interaction
  $("#messageArea").on("submit", function (event) {
    event.preventDefault();

    const date = new Date();
    const str_time = `${date.getHours()}:${date.getMinutes()}`;
    const rawText = $("#text").val();

    const userHtml = `<div class="d-flex justify-content-end mb-4">
            <div class="msg_cotainer_send">${rawText}<span class="msg_time_send">${str_time}</span></div>
            <div class="img_cont_msg"><img src="{{ img_file }}" class="rounded-circle user_img_msg"></div>
        </div>`;

    $("#text").val("");
    $("#messageFormeight").append(userHtml);

    $.ajax({
      data: { msg: rawText },
      type: "POST",
      url: "/get",
    }).done(function (data) {
      const botHtml = `<div class="d-flex justify-content-start mb-4">
                <div class="img_cont_msg"><img src="/static/chatbot icon.png" class="rounded-circle user_img_msg"></div>
                <div class="msg_cotainer">${data}<span class="msg_time">${str_time}</span></div>
            </div>`;
      $("#messageFormeight").append($.parseHTML(botHtml));
      $("#messageFormeight").css("height", "auto");

      const chatBox = document.getElementById("messageFormeight");
      chatBox.scrollTop = chatBox.scrollHeight;
    });
  });

  // Audio recording
  let mediaRecorder;
  let audioChunks = [];
  let isRecording = false;

  const recordBtn = document.getElementById("record-btn");
  const micIcon = document.getElementById("mic-icon");

  recordBtn.addEventListener("click", async () => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      alert("❌ Your browser does not support audio recording.");
      return;
    }

    if (!isRecording) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: true,
        });
        mediaRecorder = new MediaRecorder(stream);

        audioChunks = [];
        mediaRecorder.ondataavailable = (event) => {
          audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
          const formData = new FormData();
          formData.append("audio", audioBlob, "recording.webm");

          try {
            const res = await fetch("/send_audio", {
              method: "POST",
              body: formData,
            });
            const data = await res.json();

            if (data.error) {
              alert("❌ " + data.error);
              return;
            }

            const transcribedText = data.transcribed_text;
            const date = new Date();
            const str_time = `${date.getHours()}:${date.getMinutes()}`;

            const userHtml = `<div class="d-flex justify-content-end mb-4">
                            <div class="msg_cotainer_send">${transcribedText}<span class="msg_time_send">${str_time}</span></div>
                            <div class="img_cont_msg"><img src="{{ img_file }}" class="rounded-circle user_img_msg"></div>
                        </div>`;

            $("#messageFormeight").append(userHtml);
            $("#messageFormeight").css("height", "auto");

            // Send to /get as text
            const aiRes = await $.ajax({
              data: { msg: transcribedText },
              type: "POST",
              url: "/get",
            });

            const aiResponseHtml = `<div class="d-flex justify-content-start mb-4">
                            <div class="img_cont_msg"><img src="/static/chatbot icon.png" class="rounded-circle user_img_msg"></div>
                            <div class="msg_cotainer">${aiRes}<span class="msg_time">${str_time}</span></div>
                        </div>`;

            $("#messageFormeight").append($.parseHTML(aiResponseHtml));
            $("#messageFormeight").css("height", "auto");

            const chatBox = document.getElementById("messageFormeight");
            chatBox.scrollTop = chatBox.scrollHeight;
          } catch (err) {
            alert("❌ Error sending audio: " + err);
          }
        };

        mediaRecorder.start();
        isRecording = true;

        recordBtn.classList.add("recording");
        micIcon.classList.remove("fa-microphone");
        micIcon.classList.add("fa-stop");
      } catch (err) {
        alert("❌ Could not access microphone: " + err);
      }
    } else {
      mediaRecorder.stop();
      isRecording = false;

      recordBtn.classList.remove("recording");
      micIcon.classList.remove("fa-stop");
      micIcon.classList.add("fa-microphone");
    }
  });
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
  const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);

  if (isIOS && isSafari) {
    const recordBtn = document.getElementById("record-btn");
    if (recordBtn) {
      recordBtn.style.display = "none";
    }
  }
});
