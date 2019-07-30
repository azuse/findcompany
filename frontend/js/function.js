var filterOptionSearch = {
    "hasContect": 1,
    "hasAddress": 1,
    "hasHomePage": 1,
    "notLeagal": 1,
    "inFavorite": 1,
    "notFavorite": 1,
    "sort": "timeDESC",
    "shanghai": 0,
    "beijing": 0,
    "guangzhou": 0,
    "shenzhen": 0,
    "otherCities": 0
}

var filterOptionTopCompanies = {
    "hasContect": 1,
    "hasAddress": 1,
    "hasHomePage": 1,
    "notLeagal": 1,
    "inFavorite": 1,
    "notFavorite": 1,
    "sort": "timeDESC",
    "shanghai": 0,
    "beijing": 0,
    "guangzhou": 0,
    "shenzhen": 0,
    "otherCities": 0,
    "color": 0
}

var filterOptionFavoriteCompanies = {
    "hasContect": 1,
    "hasAddress": 1,
    "hasHomePage": 1,
    "notLeagal": 1,
    "inFavorite": 1,
    "notFavorite": 0,
    "sort": "favoriteDESC",
    "shanghai": 0,
    "beijing": 0,
    "guangzhou": 0,
    "shenzhen": 0,
    "otherCities": 0,
    "color": 0
}

var queryStartNumber = 0;
var queryLen = 20;

var doubleClick = 0;
var favoriteColor = restoreSession("favoriteColor")
var favoriteTime = restoreSession("favoriteTime")
var favoriteCompanies = restoreSession("favoriteCompanies")
var junkCompanies = restoreSession("junkCompanies")
var junkCompanyData = restoreSession("junkCompanyData")
var notes = restoreSession("notes")

if (favoriteColor == null) {
    favoriteColor = {}
    console.log("favoriteColor = null")
}
if (favoriteTime == null) {
    favoriteTime = {}
    console.log("favoriteTime = null")
}
if (favoriteCompanies == null) {
    favoriteCompanies = []
    console.log("favoriteCompanies = null")
}
if (junkCompanies == null) {
    junkCompanies = {}
    console.log("junkCompanies = null")
}
if (junkCompanyData == null) {
    junkCompanyData = []
    console.log("junkCompanyData = null")
}
if (notes == null) {
    notes = {}
    console.log("notes = null")
}

var junkFilter = 1
var colorNames = ['红色', '黄色', '绿色', '蓝色', '紫色', '灰色']


function favoriteOnly(companies) {

    var ret = new Array;
    for (i in companies) {
        if (favoriteColor[companies[i].id] != null && favoriteColor[companies[i].id] != 0)
            ret.push(companies[i])
    }
    return ret
}

function notfavoriteOnly(companies) {
    var ret = new Array;
    for (i in companies) {
        if (favoriteColor[companies[i].id] == null || favoriteColor[companies[i].id] == 0)
            ret.push(companies[i])
    }
    return ret
}

function junkCompaniesOnly(companies) {
    var ret = new Array;
    for (i in companies) {
        if (junkCompanies[companies[i].id] != null && junkCompanies[companies[i].id] != 0)
            ret.push(companies[i])
    }
    return ret
}

function notJunkCompaniesOnly(companies) {
    var ret = new Array;
    for (i in companies) {
        if (junkCompanies[companies[i].id] == null || junkCompanies[companies[i].id] == 0) {
            companies[i].junk = 0
            ret.push(companies[i])
        }
    }
    return ret
}

function search(query) {
    queryStartNumber = 0
    searchCompany.companies = []
    $.ajax({
        type: "post",
        url: "php/search_new_new.php",
        data: {
            start: queryStartNumber,
            len: queryLen,
            keyword: query,
            options: JSON.stringify(filterOptionSearch),
        },
        success: function (res) {
            console.log(res)
            
            $("#resultCount")[0].innerHTML = res.resultNumber
            if (res.resultNumber == 0)
            {
                $("#preloader")[0].innerHTML = "无结果"
                return
            }
            if (res.error == 1)
            {
                console.log("new search method failed, maybe flask search server isnot running?")
                search_origin(query)
            }
            if (filterOptionSearch['inFavorite'] && !filterOptionSearch['notFavorite'])
                res.data = favoriteOnly(res.data)
            if (!filterOptionSearch['inFavorite'] && filterOptionSearch['notFavorite'])
                res.data = notfavoriteOnly(res.data)
            if (filterOptionSearch['inFavorite'] && filterOptionSearch['notFavorite'])
                res.data = res.data
            if (junkFilter)
                res.data = notJunkCompaniesOnly(res.data)


            res.data = restoreNotes(res.data)
            searchCompany.companies = restoreFavorite(res.data)
            searchCompany.favoriteTime = favoriteTime
            searchCompany.$nextTick(function () {
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
        },
        error: function(jqXHR, Texterror){
            console.log(Texterror)
        }
    });
}

function search_origin(query) {
    queryStartNumber = 0
    searchCompany.companies = []
    $.ajax({
        type: "post",
        url: "php/search.php",
        timeout: 20000,
        data: {
            start: queryStartNumber,
            len: queryLen,
            keyword: query,
            options: JSON.stringify(filterOptionSearch),
        },
        success: function (res) {
            console.log(res)
            
            $("#resultCount")[0].innerHTML = res.resultNumber
            if (res.resultNumber == 0)
            {
                $("#preloader")[0].innerHTML = "无结果"
                return
            }
            if (filterOptionSearch['inFavorite'] && !filterOptionSearch['notFavorite'])
                res.data = favoriteOnly(res.data)
            if (!filterOptionSearch['inFavorite'] && filterOptionSearch['notFavorite'])
                res.data = notfavoriteOnly(res.data)
            if (filterOptionSearch['inFavorite'] && filterOptionSearch['notFavorite'])
                res.data = res.data
            if (junkFilter)
                res.data = notJunkCompaniesOnly(res.data)


            res.data = restoreNotes(res.data)
            searchCompany.companies = restoreFavorite(res.data)
            searchCompany.favoriteTime = favoriteTime
            searchCompany.$nextTick(function () {
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
        },
        error:function(jqXHR, textStatus){
            
        }
    });
}

function setOptionSearch() {
    queryStartNumber = 0
    searchCompany.companies = []
    var q = $("#search").val();
    $.ajax({
        url: "php/search_new.php",
        type: "POST",
        data: {
            options: JSON.stringify(filterOptionSearch),
            start: queryStartNumber,
            len: queryLen,
            keyword: q,
        },
        success: function (res) {
            console.log(res)
            $("#resultCount")[0].innerHTML = res.resultNumber

            if (filterOptionSearch['inFavorite'] && !filterOptionSearch['notFavorite'])
                res.data = favoriteOnly(res.data)
            if (!filterOptionSearch['inFavorite'] && filterOptionSearch['notFavorite'])
                res.data = notfavoriteOnly(res.data)
            if (filterOptionSearch['inFavorite'] && filterOptionSearch['notFavorite'])
                res.data = res.data
            if (junkFilter)
                res.data = notJunkCompaniesOnly(res.data)


            res.data = restoreNotes(res.data)
            searchCompany.companies = restoreFavorite(res.data)
            searchCompany.favoriteTime = favoriteTime
            searchCompany.$nextTick(function () {
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

            if (filterOptionSearch['inFavorite'] && !filterOptionSearch['notFavorite'] && searchCompany.companies.length == 0)
                loadMore()
        }
    })
}

function colorOnly(companies) {
    if (filterOptionFavoriteCompanies['color'] == 0)
        return companies
    else {
        var ret = new Array;
        for (i in companies) {
            if (favoriteColor[companies[i].id] == filterOptionFavoriteCompanies['color'])
                ret.push(companies[i])
        }
        return ret
    }

}

function cityOnly(companies) {
    if (filterOptionFavoriteCompanies['shanghai'] == 1) {
        var ret = new Array;
        for (i in companies) {
            if (companies[i].location.indexOf("上海") != -1)
                ret.push(companies[i])
        }
        return ret
    }
    else if (filterOptionFavoriteCompanies['beijing'] == 1) {
        var ret = new Array;
        for (i in companies) {
            if (companies[i].location.indexOf("北京") != -1)
                ret.push(companies[i])
        }
        return ret
    }
    else if (filterOptionFavoriteCompanies['guangzhou'] == 1) {
        var ret = new Array;
        for (i in companies) {
            if (companies[i].location.indexOf("广州") != -1)
                ret.push(companies[i])
        }
        return ret
    }
    else if (filterOptionFavoriteCompanies['shenzhen'] == 1) {
        var ret = new Array;
        for (i in companies) {
            if (companies[i].location.indexOf("深圳") != -1)
                ret.push(companies[i])
        }
        return ret
    }
    else if (filterOptionFavoriteCompanies['otherCities'] == 1) {
        var ret = new Array;
        for (i in companies) {
            if (companies[i].location.indexOf("深圳") == -1 && companies[i].location.indexOf("广州") == -1 && companies[i].location.indexOf("上海") == -1 && companies[i].location.indexOf("北京") == -1)
                ret.push(companies[i])
        }
        return ret
    }
    else
        return companies
}

function favoriteOrderByTimeDESC(companies) {
    var len = companies.length
    var ret = new Array

    if (len == 0)
        return ret

    var i = 0

    while (i < len) {
        var maxTime = favoriteTime[companies[i].id];
        var maxCom = i;
        var j = i;
        while (j < len) {
            if (favoriteTime[companies[j].id] > maxTime) {
                maxTime = favoriteTime[companies[j].id]
                maxCom = j
            }
            j++
        }
        ret.push(companies[maxCom])
        companies[maxCom] = companies[i]
        i++
    }

    return ret
}

function favoriteOrderByTimeASC(companies) {
    var len = companies.length
    var ret = new Array

    if (len == 0)
        return ret

    var i = 0

    while (i < len) {
        var j = i;
        var minTime = favoriteTime[companies[i].id];
        var minCom = i;
        while (j < len) {
            if (favoriteTime[companies[j].id] < minTime) {
                minTime = favoriteTime[companies[j].id]
                minCom = j
            }
            j++
        }

        ret.push(companies[minCom])
        companies[minCom] = companies[i]
        i++
    }

    return ret
}

function favoriteOrderByAddTimeDESC(companies) {
    var len = companies.length
    var ret = new Array

    if (len == 0)
        return ret

    var i = 0

    while (i < len) {
        var maxTime = new Date(companies[i].addDate).getTime();
        var maxCom = i;
        var j = i;
        while (j < len) {
            if (new Date(companies[j].addDate).getTime() > maxTime) {
                maxTime = new Date(companies[j].addDate).getTime()
                maxCom = j
            }
            j++
        }
        ret.push(companies[maxCom])
        companies[maxCom] = companies[i]
        i++
    }

    return ret
}

function favoriteOrderByAddTimeASC(companies) {
    var len = companies.length
    var ret = new Array

    if (len == 0)
        return ret

    var i = 0

    while (i < len) {
        var j = i;
        var minTime = new Date(companies[i].addDate).getTime();
        var minCom = i;
        while (j < len) {
            if (new Date(companies[j].addDate).getTime() < minTime) {
                minTime = new Date(companies[j].addDate).getTime()
                minCom = j
            }
            j++
        }

        ret.push(companies[minCom])
        companies[minCom] = companies[i]
        i++
    }

    return ret
}

function setOptionFavoriteCompanies() {
    res = favoriteCompanies

    if (filterOptionFavoriteCompanies['inFavorite'] && !filterOptionFavoriteCompanies['notFavorite'])
        res = favoriteOnly(res)
    if (!filterOptionFavoriteCompanies['inFavorite'] && filterOptionFavoriteCompanies['notFavorite'])
        res = notfavoriteOnly(res)
    if (filterOptionFavoriteCompanies['inFavorite'] && filterOptionFavoriteCompanies['notFavorite'])
        res = res
    if (junkFilter)
        res = notJunkCompaniesOnly(res)

    if (filterOptionFavoriteCompanies['sort'] == "favoriteDESC")
        res = favoriteOrderByTimeDESC(res)
    else if (filterOptionFavoriteCompanies['sort'] == "favoriteASC")
        res = favoriteOrderByTimeASC(res)
    else if (filterOptionFavoriteCompanies['sort'] == "timeASC")
        res = favoriteOrderByAddTimeASC(res)
    else if (filterOptionFavoriteCompanies['sort'] == "timeDESC")
        res = favoriteOrderByAddTimeDESC(res)

    res = colorOnly(res)
    res = cityOnly(res)
    res = restoreNotes(res)
    favoriteCompany.companies = restoreFavorite(res)
    favoriteCompany.favoriteTime = favoriteTime
    favoriteCompany.$nextTick(function () {
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

        console.log('render finished')

    })
}

function setOptionTopCompanies() {
    queryStartNumber = 0
    $.ajax({
        url: "../php/topCompany.php",
        type: "POST",
        async: false,
        data: {
            options: JSON.stringify(filterOptionTopCompanies),
            start: queryStartNumber,
            len: queryLen
        },
        success: function (res) {
            console.log(res)
            if (filterOptionTopCompanies['inFavorite'] && !filterOptionTopCompanies['notFavorite'])
                res.data = favoriteOnly(res.data)
            if (!filterOptionTopCompanies['inFavorite'] && filterOptionTopCompanies['notFavorite'])
                res.data = notfavoriteOnly(res.data)
            if (filterOptionTopCompanies['inFavorite'] && filterOptionTopCompanies['notFavorite'])
                res.data = res.data
            if (junkFilter)
                res.data = notJunkCompaniesOnly(res.data)

            res.data = colorOnly(res.data)
            res.data = restoreNotes(res.data)

            topCompany.companies = restoreFavorite(res.data)
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

                console.log(this.companies)
                console.log('render finished')

            })

        }
    })

}

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

function saveFavorite() {
    saveSession("favoriteColor", favoriteColor)
    saveSession("favoriteTime", favoriteTime)
    saveSession("favoriteCompanies", favoriteCompanies)
}

function restoreFavorite(companies) {

    for (i in companies) {
        if (favoriteColor[companies[i].id] == null)
            companies[i].favorite = 0
        else
            companies[i].favorite = favoriteColor[companies[i].id]
    }
    return companies
}

function saveNotes(note, companyId) {
    notes[companyId] = note
    saveSession("notes", notes)
}

function restoreNotes(companies) {
    for (i in companies) {
        if (notes[companies[i].id] == null)
            companies[i].note = ""
        else
            companies[i].note = notes[companies[i].id]
    }
    return companies
}



function change_my_class(event) {
    if ($(event.target).hasClass("chip-custom-selected"))
        $(event.target).removeClass("chip-custom-selected")
    else
        $(event.target).addClass('chip-custom-selected')
}

function set_my_parents_children_class_to_not(event) {
    $(event.target.parentNode.children).removeClass('chip-custom-selected');
}

function set_my_class_to_selected(event) {
    $(event.target).addClass('chip-custom-selected');
}

function set_all_filter_cities_to_none(filterOption) {
    filterOption['shanghai'] = 0
    filterOption['beijing'] = 0
    filterOption['guangzhou'] = 0
    filterOption['shenzhen'] = 0
    filterOption['otherCities'] = 0
}

function add_to_junk_companies(companyId, companyData) {
    junkCompanies[companyId] = 1
    junkCompanyData.push(companyData)
    saveSession('junkCompanies', junkCompanies)
    saveSession('junkCompanyData', junkCompanyData)
}

function remove_from_junk_companies(companyId) {
    junkCompanies[companyId] = 0
    ret = []
    for (i in junkCompanyData) {
        if (junkCompanyData[i].id != companyId)
            ret.push(junkCompanyData[i])
    }
    junkCompanyData = ret
    saveSession('junkCompanies', junkCompanies)
    saveSession('junkCompanyData', junkCompanyData)
}

function decode_utf8(s) {
    return eval(s);
}


function address2geolocation(address) {
    var gpslocation = "not found";

    $.ajax({
        url: "php/geolocation.php",
        async: false,
        type: "get",
        data: {
            address: address,
        },
        success: function (res) {
            jsonData = JSON.parse(res)
            gpslocation = jsonData.result.location
        },
        fail: function () {
            console.log("ajax fail")
        }
    })

    return gpslocation
}

var modalKey = 0

var companyModal = new Vue({
    el: "#companyModal",
    data: {
        company: {},
        contects: [],
        maimai: [],
        favoriteTime: favoriteTime,
        searchCompaniesKey: 0
    },
    methods: {
        switchFavorite: function (id, favorite, color) {
            if (color == favorite) {
                return
            }
            else if (color != 0) {

                if (typeof searchCompany !== 'undefined' && typeof searchCompany.companies[this.searchCompaniesKey] !== 'undefined')
                    searchCompany.companies[this.searchCompaniesKey].favorite = color
                if (typeof favoriteCompany !== 'undefined')
                    favoriteCompany.companies[this.searchCompaniesKey].favorite = color
                if (typeof topCompany !== 'undefined')
                    topCompany.companies[this.searchCompaniesKey].favorite = color

                this.company.favorite = color

                favoriteColor[id] = color
                favoriteTime[id] = Date.now()
                var tmp = []
                for (i in favoriteCompanies) {
                    if (favoriteCompanies[i].id != this.company.id)
                        tmp.push(favoriteCompanies[i])
                }
                tmp.push(this.company)
                favoriteCompanies = tmp
                saveFavorite()

                Materialize.toast('已添加到收藏(' + colorNames[color - 1] + ')，可在收藏夹中查看', 1000)
            }
            else {
                if (typeof searchCompany !== 'undefined' && typeof searchCompany.companies[this.searchCompaniesKey] !== 'undefined')
                    searchCompany.companies[this.searchCompaniesKey].favorite = 0
                if (typeof favoriteCompany !== 'undefined')
                    favoriteCompany.companies[this.searchCompaniesKey].favorite = 0
                if (typeof topCompany !== 'undefined')
                    favoriteCompany.companies[this.searchCompaniesKey].favorite = color

                this.company.favorite = 0
                var tmp = []
                for (i in favoriteCompanies) {
                    if (favoriteCompanies[i].id != this.company.id)
                        tmp.push(favoriteCompanies[i])
                }
                favoriteCompanies = tmp

                favoriteColor[id] = 0
                saveFavorite()

                Materialize.toast('已从收藏中删除', 800)
            }

            return
        },
        junkCompany: function (id) {
            add_to_junk_companies(id, this.company)
            if (typeof searchCompany !== 'undefined')
                searchCompany.companies[modalKey].junk = 1
            if (typeof favoriteCompany !== 'undefined')
                favoriteCompany.companies[modalKey].junk = 1
            if (typeof topCompany !== 'undefined')
                topCompany.companies[modalKey].junk = 1


            Materialize.toast('已标记为无效信息', 800);
            $("#companyModal").modal('close')
        },
        showMap: function () {
            gpslocation = address2geolocation(this.company.address)
            if (gpslocation == "not found")
                console.log("not found")
            else {
                $("#map").css("display", "block");
                var map = new BMap.Map("map");
                var point = new BMap.Point(gpslocation.lng, gpslocation.lat);  // 创建点坐标  
                map.addControl(new BMap.NavigationControl());
                map.addControl(new BMap.ScaleControl());
                map.addControl(new BMap.OverviewMapControl());
                map.addControl(new BMap.MapTypeControl());
                var marker = new BMap.Marker(point);        // 创建标注    
                map.addOverlay(marker);
                map.centerAndZoom(point, 13);
            }

        },
        saveNote: function () {
            saveNotes(this.company.note, this.company.id)
            Materialize.toast("备注已保存", 800)
            console.log(notes)
        }
    }
})

function change_result_display_number(number) {
    $("#resultSelectBtn")[0].innerHTML = number
    queryLen = number
    if (typeof searchCompany != "undefined")
        setOptionSearch()
    if (typeof favoriteCompany != "undefined")
        setOptionFavoriteCompanies()
    if (typeof topCompany != "undefined")
        setOptionTopCompanies()

}

function JSONToCSVConvertor(JSONData, ShowLabel) {

    //If JSONData is not an object then JSON.parse will parse the JSON string in an Object
    var arrData = typeof JSONData != 'object' ? JSON.parse(JSONData) : JSONData;
    var CSV = '';
    //This condition will generate the Label/Header
    if (ShowLabel) {
        var row = "";

        //This loop will extract the label from 1st index of on array
        for (var index in arrData[0]) {
            //Now convert each value to string and comma-seprated
            row += index + ',';
        }
        row = row.slice(0, -1);
        //append Label row with line break
        CSV += row + '\r\n';
    }

    //1st loop is to extract each row
    for (var i = 0; i < arrData.length; i++) {
        var row = "";
        //2nd loop will extract each column and convert it in string comma-seprated
        for (var index in arrData[i]) {
            row += '"' + arrData[i][index] + '",';
        }
        row.slice(0, row.length - 1);
        //add a line break after each row
        CSV += row + '\r\n';
    }

    if (CSV == '') {
        alert("Invalid data");
        return;
    }

    //this trick will generate a temp "a" tag
    var link = document.createElement("a");
    link.id = "lnkDwnldLnk";

    //this part will append the anchor tag and remove it after automatic click
    document.body.appendChild(link);

    var csv = CSV;
    var csvUrl = encodeURI("data:text/csv;charset=utf-8,\uFEFF" + csv)
    var filename = 'UserExport.csv';
    $("#lnkDwnldLnk")
        .attr({
            'download': filename,
            'href': csvUrl
        });

    $('#lnkDwnldLnk')[0].click();
    document.body.removeChild(link);
}

function unicode(text){
    var r = /u([\d\w]{4})/gi;
    text = text.replace(r, function (match, grp) {
        return String.fromCharCode(parseInt(grp, 16)); } );
    text = unescape(text);
    return text
}

