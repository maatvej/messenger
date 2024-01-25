// static/js/clearable_file_input.js
document.addEventListener('DOMContentLoaded', function () {
    var fileInput = document.querySelector('.clearablefileinput');
    var label = fileInput.nextElementSibling;

    fileInput.addEventListener('change', function () {
        var fileName = fileInput.value.split('\\').pop();
        label.setAttribute('data-text', fileName);
    });
});
