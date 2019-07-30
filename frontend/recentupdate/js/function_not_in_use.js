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
    "otherCities": 0
}

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

var queryStartNumber = 0;
var queryLen = 100;

var doubleClick = 0;
var favoriteColor = restoreSession("favoriteColor")
var favoriteTime = restoreSession("favoriteTime")
var junkCompanies = restoreSession("junkCompanies")
if (favoriteColor == null) {
    favoriteColor = {}
    console.log("favoriteColor = null")
}
if (favoriteTime == null) {
    favoriteTime = {}
    console.log("favoriteTime = null")
}
if (junkCompanies == null) {
    junkCompanies = {}
    console.log("junkCompanies = null")
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
        if (junkCompanies[companies[i].id] == null || junkCompanies[companies[i].id] == 0)
            ret.push(companies[i])
    }
    return ret
}

function setOptionTopCompanies() {
    queryStartNumber = 0
    $.ajax({
        url: "../php/topCompany.php",
        type: "POST",
        data: {
            options: JSON.stringify(filterOptionTopCompanies),
            start: queryStartNumber,
            len: queryLen
        },
        success: function (res) {
            console.log(res)

            // res = favoriteOnly(res)
            if (filterOptionTopCompanies['inFavorite'] && !filterOptionTopCompanies['notFavorite'])
                res = favoriteOnly(res)
            if (!filterOptionTopCompanies['inFavorite'] && filterOptionTopCompanies['notFavorite'])
                res = notfavoriteOnly(res)
            if (filterOptionTopCompanies['inFavorite'] && filterOptionTopCompanies['notFavorite'])
                res = res
            if (junkFilter)
                res = notJunkCompaniesOnly(res)


            topCompany.companies = restoreFavorite(res)
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

                if($("#topCompanyContainer ul")[0].children.length < 50)
                    loadMore()
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

function saveFavorite(companies) {
    for (i in companies) {
        favoriteColor[companies[i].id] = companies[i].favorite
    }
    saveSession("favoriteColor", favoriteColor)
    saveSession("favoriteTime", favoriteTime)
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

function add_to_junk_companies(companyId) {
    junkCompanies[companyId] = 1
    saveSession('junkCompanies', junkCompanies)
}

function remove_from_junk_companies(companyId) {
    junkCompanies[companyId] = 0
    saveSession('junkCompanies', junkCompanies)
}

function loadMore() {
    queryStartNumber += queryLen
    $.ajax({
        url: "../php/topCompany.php",
        type: "POST",
        data: {
            options: JSON.stringify(filterOptionTopCompanies),
            start: queryStartNumber,
            len: queryLen
        },
        success: function (res) {
            console.log(res)
            if(res == null){
                console.log("load end")
                Materialize.toast("已加载全部结果", 800)
                return
            }
            // res = favoriteOnly(res)
            if (filterOptionTopCompanies['inFavorite'] && !filterOptionTopCompanies['notFavorite'])
                res = favoriteOnly(res)
            if (!filterOptionTopCompanies['inFavorite'] && filterOptionTopCompanies['notFavorite'])
                res = notfavoriteOnly(res)
            if (filterOptionTopCompanies['inFavorite'] && filterOptionTopCompanies['notFavorite'])
                res = res
            if (junkFilter)
                res = notJunkCompaniesOnly(res)

            newCompanies = restoreFavorite(res)
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

                if($("#topCompanyContainer ul")[0].children.length < 50)
                    loadMore()
            })
        }
    })
}

function address2geolocation(address){
    var gpslocation = "not found";

    $.ajax({
        url: "../php/geolocation.php",
        async: false,
        type: "get",
        data: {
            address: address,
        },
        success: function (res) {
            jsonData = JSON.parse(res)
            gpslocation = jsonData.result.location
        },
        fail: function (){
            console.log("ajax fail")
        }
    })

    return gpslocation
}