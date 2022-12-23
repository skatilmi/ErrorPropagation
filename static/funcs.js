function convertSVGToPNG(svgElement) {
    // Create a canvas element
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    // Set the dimensions of the canvas to the dimensions of the SVG image
    canvas.width = svgElement.clientWidth;
    canvas.height = svgElement.clientHeight;

    // Create an image element and set its source to the SVG code
    const img = new Image();
    img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgElement.innerHTML)));

    // Draw the image onto the canvas
    ctx.drawImage(img, 0, 0);

    // Return the data URL of the canvas
    return canvas.toDataURL();
}

function downloadPNG(png) {
    // Create a link element and set its href to the PNG data URL
    const link = document.createElement('a');
    link.href = png;
    link.download = 'image.png';

    // Add the link to the document and click it to trigger the download
    document.body.appendChild(link);
    link.click();

    // Remove the link from the document
    document.body.removeChild(link);
}

function downloadSVGAsPNG(buttonElement, scale) {
    var svgElement = buttonElement.parentElement.querySelector('.renderLatex > mjx-container > svg');
    _downloadSVGAsPNG(svgElement, buttonElement, scale);
}


function copyCode(el) {
    //var codeElement = el.nextElementSibling;
    var codeElement = el.previousElementSibling;
    var textarea = document.createElement('textarea');
    textarea.value = codeElement.textContent;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
}

function downloadSVGAsPNG2(buttonElement, scale) {
    var svgElement = buttonElement.parentElement.parentElement.querySelector('.render-latex > button:nth-child(1) > mjx-container > svg');
    console.log(buttonElement.parentElement.parentElement)
    _downloadSVGAsPNG(svgElement, buttonElement, scale);

}

function copyCode2(button) {
    // Get the content of the button
    var element = button.parentElement.parentElement.querySelector('.raw-latex > button');
    var text = element.innerText;



    // Create a temporary textarea element
    const textarea = document.createElement("textarea");
    textarea.value = text;
    document.body.appendChild(textarea);

    // Select the text in the textarea
    textarea.select();

    // Copy the selected text to the clipboard
    document.execCommand("copy");

    // Remove the textarea element
    document.body.removeChild(textarea);
    const message = document.createElement("div");
    message.innerText = "Copied to clipboard!";
    message.style.position = "absolute";
    message.style.top = "50%";
    message.style.left = "50%";
    message.style.transform = "translate(-50%, -50%)";
    message.style.backgroundColor = "lightgray";
    message.style.padding = "1em";
    message.style.borderRadius = "5px";
    message.style.boxShadow = "2px 2px 10px rgba(0, 0, 0, 0.1)";
    document.body.appendChild(message);

    // Remove the message after a few seconds
    setTimeout(function () {
        document.body.removeChild(message);
    }, 2000);
}



function _downloadSVGAsPNG(svgElement, buttonElement, scale) {

    buttonElement.addEventListener('click', function () {
        var canvas = document.createElement('canvas');
        var ctx = canvas.getContext('2d');

        // Set the canvas size to the scaled size of the SVG image
        canvas.width = svgElement.width.baseVal.value * scale;
        canvas.height = svgElement.height.baseVal.value * scale;

        var img = new Image();
        img.onload = function () {
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            canvas.toBlob(function (blob) {
                var url = URL.createObjectURL(blob);
                var a = document.createElement('a');
                a.download = 'image.png';
                a.href = url;
                a.click();

            });
        };
        img.src = 'data:image/svg+xml;base64,' + btoa(svgElement.outerHTML);
    });
}

