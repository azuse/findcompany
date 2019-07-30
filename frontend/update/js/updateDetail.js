
function exportResult() {
    var workbook = XLSX.utils.table_to_book(document.getElementsByClassName('excelTable')[0], { type: 'string' });
    XLSX.writeFile(workbook, 'out.xlsx', { bookType: "xlsx", });
}

var topCompany = new Vue({
    el: '#topCompanyContainer',
    data: {
        companies: [],
        favoriteTime: favoriteTime,
        companyCount: 0
    },
    created: function () {
        // `this` 指向 vm 实例
    },
    methods: {
        switchFavorite: function (id, favorite, key, color) {
            if (color == favorite) {
                this.companies[key].favorite = 0
                favoriteColor[id] = 0

                saveFavorite(this.companies)
                Materialize.toast('已从收藏中删除', 800)
            }
            else if (color != 0) {
                this.companies[key].favorite = color
                favoriteColor[id] = color
                favoriteTime[id] = Date.now()

                saveFavorite(this.companies)
                Materialize.toast('已添加到收藏(' + colorNames[color - 1] + ')，可在收藏夹中查看', 1000)
            }
            else {
                this.companies[key].favorite = 0
                favoriteColor[id] = 0

                saveFavorite(this.companies)
                Materialize.toast('已从收藏中删除', 800)
            }
            return
        },
        formatDate: function (date) {
            var d = new Date(date);
            var year = d.getFullYear();
            var month = d.getMonth() + 1;
            month = month < 10 ? "0" + month : "" + month;
            var day = d.getDate() < 10 ? '0' + d.getDate() : '' + d.getDate();
            var hour = d.getHours();
            hour = hour < 10 ? "0" + hour : "" + hour;
            var minutes = d.getMinutes();
            minutes = minutes < 10 ? "0" + minutes : + minutes;
            var seconds = d.getSeconds();
            seconds = seconds < 10 ? "0" + seconds : + seconds;
            return year + '-' + month + '-' + day + ' ' + hour + ':' + minutes + ':' + seconds;
        },
        isFavorite: function (id) {
            if (favoriteColor[id] != null && favoriteColor[id] != 0)
                return true
            else
                return false
        },
        junkCompany: function (id, key) {
            add_to_junk_companies(id, this.companies[key])
            this.companies[key].junk = 1
            Materialize.toast('已标记为无效信息', 800);
        },
        openModal: function (key) {
            modalKey = key
            companyModal.company = this.companies[key]
            console.log(this.companies[key].contectAllJson.replace(/(\r\n|\n|\r)/gm, ""))
            contect = eval(this.companies[key].contectAllJson.replace(/(\r\n|\n|\r)/gm, ""))
            for (i in contect) {
                try {
                    eval("contect[i].name = '" + contect[i].name.replace(/u/g, "\\u") + "'")
                }
                catch (err) {
                    console.log(err)
                }
                try {
                    eval("contect[i].position = '" + contect[i].position.replace(/u/g, "\\u") + "'")
                }
                catch (err) {
                    console.log(err)
                }
                try {
                    eval("contect[i].tel = '" + contect[i].tel.replace(/u/g, "\\u") + "'")
                }
                catch (err) {
                    console.log(err)
                }
                try {
                    eval("contect[i].phone = '" + contect[i].phone.replace(/u/g, "\\u") + "'")
                }
                catch (err) {
                    console.log(err)
                }
            }
            companyModal.contects = contect
            companyModal.searchCompaniesKey = key
            switch (this.companies[key].favorite) {
                case 1:
                    $("#favorite-modal-red")[0].checked = true;
                    break
                case 2:
                    $("#favorite-modal-yellow")[0].checked = true;
                    break
                case 3:
                    $("#favorite-modal-green")[0].checked = true;
                    break
                case 4:
                    $("#favorite-modal-blue")[0].checked = true;
                    break
                case 5:
                    $("#favorite-modal-purple")[0].checked = true;
                    break
                case 6:
                    $("#favorite-modal-grey")[0].checked = true;
                    break
                case 0:
                    $("#favorite-modal-no")[0].checked = true;
                    break
            }
            $("#map").css("display", "none")
            companyModal.maimai = null
            $.ajax({
                url: "../php/maimai.php",
                data: {
                    "company": this.companies[key].company
                },
                success: function (res) {

                    companyModal.maimai = res
                }
            })

            $("#companyModal").modal('open')
            $("#companyModal").scrollTop(0)
        },
        saveNote: function (note, id) {
            saveNotes(note, id)
            Materialize.toast("备注已保存", 800)
            console.log(notes)
        }
    }

})


var excelTableVue = new Vue({
    el: "#excelTable",
    data: {
        companies: []
    },
    methods: {
        length: function (array) {
            return array.length
        }
    }

})

function openExcelModal() {
    excelTableVue.companies = topCompany.companies
    $("#excelModal").modal('open')
}



$('.modal').modal();

$('.button-collapse').sideNav({
    menuWidth: 300, // Default is 240
    edge: 'left', // Choose the horizontal origin
    closeOnClick: false, // Closes side-nav on <a> clicks, useful for Angular/Meteor
    draggable: true // Choose whether you can drag to open on touch screens
}
);
$('select').material_select();

$('.dropdown-button-custom').dropdown({
    inDuration: 300,
    outDuration: 225,
    constrain_width: false, // Does not change width of dropdown to that of the activator
    hover: true, // Activate on hover
    gutter: 0, // Spacing from edge
    belowOrigin: true, // Displays dropdown below the button
    alignment: 'left' // Displays dropdown with edge aligned to the left of button
}
);


var url_string = window.location.href
var url = new URL(url_string);
var addId = url.searchParams.get("addId");

var junkFilter = 1

$.ajax({
    url:"../php/updateDetail.php",
    data:{
        "addId":addId
    },
    success:function(res){
        console.log(res)
            if(res == null){
                console.log("load end")
                Materialize.toast("已加载全部结果", 800)
                $("#load-more-btn")[0].innerHTML = "已加载全部结果"
                $("#load-more-btn").addClass("disabled")
                return
            }
            if (junkFilter)
                res.data = notJunkCompaniesOnly(res.data)

                res.data = restoreNotes(res.data)
            newCompanies = restoreFavorite(res.data)
            for (i in newCompanies) {
                topCompany.companies.push(newCompanies[i])
            }
            topCompany.favoriteTime = favoriteTime
            topCompany.$nextTick(function () {
                $('.dropdown-button-custom2').dropdown({
                    inDuration: 300,
                    outDuration: 225,
                    constrain_width: false, // Does not change width of dropdown to that of the activator
                    hover: false, // Activate on hover
                    gutter: 0, // Spacing from edge
                    belowOrigin: true, // Displays dropdown below the button
                    alignment: 'left' // Displays dropdown with edge aligned to the left of button
                }
                );

                $('.tooltipped').tooltip({ delay: 50 });

            })
    }
})