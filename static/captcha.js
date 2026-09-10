(() => {
	const promptEl = document.getElementById("prompt");
	const imageEl = document.getElementById("captcha-image");
	const feedbackEl = document.getElementById("feedback");
	const captchaPanel = document.getElementById("captcha-panel");
	const successPanel = document.getElementById("success-panel");

	let currentChallengeId = null;

	function showChallenge(data) {
		currentChallengeId = data.challenge_id;
		promptEl.textContent = data.prompt;
		imageEl.src = data.image;
		feedbackEl.textContent = "";
		feedbackEl.classList.remove("wrong");
	}

	async function fetchChallenge() {
		const response = await fetch("/api/challenge");
		const data = await response.json();
		showChallenge(data);
	}

	function showSuccess() {
		captchaPanel.classList.add("hidden");
		successPanel.classList.remove("hidden");
	}

	async function submitClick(x, y) {
		const response = await fetch("/api/verify", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ challenge_id: currentChallengeId, x, y }),
		});
		const data = await response.json();

		if (data.success) {
			showSuccess();
			return;
		}

		feedbackEl.textContent = "Not quite, try again with a new challenge.";
		feedbackEl.classList.add("wrong");
		if (data.next) {
			showChallenge(data.next);
		} else {
			fetchChallenge();
		}
	}

	imageEl.addEventListener("click", (event) => {
		if (!currentChallengeId) {
			return;
		}
		const rect = imageEl.getBoundingClientRect();
		const scaleX = imageEl.naturalWidth / rect.width;
		const scaleY = imageEl.naturalHeight / rect.height;
		const x = Math.round((event.clientX - rect.left) * scaleX);
		const y = Math.round((event.clientY - rect.top) * scaleY);
		submitClick(x, y);
	});

	fetchChallenge();
})();
