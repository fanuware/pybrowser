document.getElementById("menu_upload").onchange = function () {
    document.getElementById("upload_form").submit();
};



/* modal: insert folder */
var modalF = document.getElementById('modalInsertFolder');
var btn = document.getElementById("insertFolder");
var close = document.getElementsByClassName("close")[0];
btn.onclick = function() {
    modalF.style.display = "block";
}
close.onclick = function() {
    modalF.style.display = "none";
}
window.onclick = function(event) {
    if (event.target == modalF) {
        modalF.style.display = "none";
    }
}
document.getElementById("insertFolderSubmit").onclick = function() {
    document.getElementById("insertFolderPath").value = (
        document.getElementById("pathname").innerHTML +
        document.getElementById("sep").innerHTML +
        document.getElementById("foldername").value
    );
    document.getElementById("sendFolder").submit();
};


/* modal: rename */
var modal = document.getElementById('modalRename');
for(var i = 0; i < document.getElementsByClassName("rename").length; i++) {
    var btn = document.getElementsByClassName("rename").item(i);
    btn.onclick = function() {
        var fullname = this.getAttribute("value");
        var filename = fullname.slice(fullname.lastIndexOf("/")+1,fullname.size)
        document.getElementById("newname").setAttribute("value", filename);
        document.getElementById("renamePath").setAttribute("value", this.getAttribute("value"));
        modal.style.display = "block";
    }
}

var close = document.getElementsByClassName("close")[1];
close.onclick = function() {
    modal.style.display = "none";
}
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}
document.getElementById("RenameSubmit").onclick = function() {
    document.getElementById("path").value = (
        document.getElementById("pathname").innerHTML +
        document.getElementById("sep").innerHTML +
        document.getElementById("path").value
    );
    document.getElementById("pathname").innerHTML = document.getElementById("path").value;
    document.getElementById("sendFolder").submit();
};

