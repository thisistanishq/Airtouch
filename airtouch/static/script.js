document.addEventListener('DOMContentLoaded', function() {
    const preloader = document.getElementById('preloader');
    const preloaderText = document.getElementById('preloader-text');
    const words = ["Hello", "Bonjour", "Ciao", "Olà", "やあ", "Hallå", "Guten tag", "Hallo", "Namaskaram", "Vanakkam"];
    let index = 0;

    function updatePreloaderText() {
        preloaderText.textContent = words[index];
        index = (index + 1) % words.length;
    }

    updatePreloaderText(); // Show first word immediately
    const textInterval = setInterval(updatePreloaderText, 150);

    setTimeout(function() {
        clearInterval(textInterval);
        preloader.style.display = 'none';
        document.getElementById('homePage').style.display = 'block';
    }, 3000);
});

function showInstructions() {
    document.getElementById('homePage').style.display = 'none';
    document.getElementById('instructionsPage').style.display = 'block';
}

function showProject() {
    document.getElementById('instructionsPage').style.display = 'none';
    document.getElementById('projectPage').style.display = 'block';
}
