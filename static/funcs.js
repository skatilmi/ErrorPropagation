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
    console.log(svgElement);

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
