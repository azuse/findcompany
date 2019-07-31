function saveSession(name, data) {
    jsonData = JSON.stringify(data)
    localStorage.setItem(name, jsonData);
}

function restoreSession(name) {
    jsonData = localStorage.getItem(name);
    try {
        data = JSON.parse(jsonData)
    }
    catch (err) {
        console.log(err)
        data = null
    }
    return data
}

$('.button-collapse').sideNav({
    menuWidth: 300, // Default is 240
    edge: 'left', // Choose the horizontal origin
    closeOnClick: false, // Closes side-nav on <a> clicks, useful for Angular/Meteor
    draggable: true // Choose whether you can drag to open on touch screens
}
);

var favoriteColor = restoreSession("favoriteColor")
var favoriteTime = restoreSession("favoriteTime")
var favoriteCompanies = restoreSession("favoriteCompanies")
var junkCompanies = restoreSession("junkCompanies")
var junkCompanyData = restoreSession("junkCompanyData")
var notes = restoreSession("notes")

var backup = {}
backup['favoriteColor'] = favoriteColor
backup['favoriteTime'] = favoriteTime
backup['favoriteCompanies'] = favoriteCompanies
backup['junkCompanies'] = junkCompanies
backup['junkCompanyData'] = junkCompanyData
backup['notes'] = notes
$("#backup-text").val(JSON.stringify(backup))
$("#download")[0].href = 'data:text/plain;charset=utf-8,' + encodeURIComponent(JSON.stringify(backup))
$("#download")[0].download = "backup.txt"
function copy(){
    navigator.clipboard.writeText(JSON.stringify(backup)).then(function() {
        console.log('Async: Copying to clipboard was successful!');
        Materialize.toast("复制成功", 800)
      }, function(err) {
        console.error('Async: Could not copy text: ', err);
        Materialize.toast("复制失败", 800)
    })
}

$("#file").on("change", function() {
    upload()
})

function upload(){
    var fileInput = $('#file');
    if (!window.FileReader) {
        alert('浏览器不支持！');
        return false;
    }
    var input = fileInput.get(0);

    // Create a reader object
    var reader = new FileReader();
    if (input.files.length) {
        var textFile = input.files[0];
        // Read the file
        reader.readAsText(textFile);
        // When it's loaded, process it
        $(reader).on('load', processFile);
    } else {
    } 
};

function processFile(e) {
    var file = e.target.result,
        results;
    text = file
    try{
        restore = JSON.parse(text)

        favoriteColor = restore['favoriteColor']
        favoriteTime = restore['favoriteTime']
        favoriteCompanies = restore['favoriteCompanies']
        junkCompanies = restore['junkCompanies']
        junkCompanyData = restore['junkCompanyData']
        notes = restore['notes']

        saveSession("favoriteColor", favoriteColor)
        saveSession("favoriteTime", favoriteTime)
        saveSession("favoriteCompanies", favoriteCompanies)
        saveSession("junkCompanies", junkCompanies)
        saveSession("junkCompanyData", junkCompanyData)
        saveSession("notes", notes)
        
        Materialize.toast("恢复成功", 800)
    }
    catch{
        Materialize.toast("数据错误", 800)

    }
}

function restore(){
    text = $("#restore-text").val()
    try{
        restore = JSON.parse(text)

        favoriteColor = restore['favoriteColor']
        favoriteTime = restore['favoriteTime']
        favoriteCompanies = restore['favoriteCompanies']
        junkCompanies = restore['junkCompanies']
        junkCompanyData = restore['junkCompanyData']
        notes = restore['notes']

        saveSession("favoriteColor", favoriteColor)
        saveSession("favoriteTime", favoriteTime)
        saveSession("favoriteCompanies", favoriteCompanies)
        saveSession("junkCompanies", junkCompanies)
        saveSession("junkCompanyData", junkCompanyData)
        saveSession("notes", notes)
        
        Materialize.toast("恢复成功", 800)
    }
    catch{
        Materialize.toast("数据错误", 800)

    }
}