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
                saveFavorite(this.companies)
                Materialize.toast('已从收藏中删除', 800)
            }
            else if (color != 0) {
                this.companies[key].favorite = color
                favoriteTime[id] = Date.now()
                saveFavorite(this.companies)
                Materialize.toast('已添加到收藏('+colorNames[color-1]+')，可在收藏夹中查看', 1000)
            }
            else {
                this.companies[key].favorite = 0
                saveFavorite(this.companies)
                Materialize.toast('已从收藏中删除，可以在垃圾桶中恢复', 800)
            }
            return
        },
        formatDate: function(date) {
            var d = new Date(date);
            var year = d.getFullYear();
            var month = d.getMonth() + 1;
            month = month < 10 ? "0" + month : "" + month;
            var day = d.getDate() < 10 ? '0' + d.getDate() : '' + d.getDate();
            var hour = d.getHours();
            hour = hour < 10 ? "0" + hour : "" + hour;
            var minutes = d.getMinutes();
            minutes = minutes < 10 ? "0" + minutes :  + minutes;
            var seconds = d.getSeconds();
            seconds = seconds < 10 ? "0" + seconds :  + seconds;
            return year + '-' + month + '-' + day + ' ' + hour + ':' + minutes + ':' + seconds;
        },
        isFavorite: function(id){
            if(favoriteColor[id] != null && favoriteColor[id] != 0 )
                return true
            else
                return false
        },
        junkCompany: function(id){
            add_to_junk_companies(id, this.companies[key])
            this.companies[key].junk = 1
            Materialize.toast('已标记为无效信息', 800);
        },
        restore: function(id){
            remove_from_junk_companies(id)
            Materialize.toast('已恢复', 1000);
            setOptionTopCompanies();
        }

    }

})

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


$(function () {
    $(".auto_submit_item").change(function () {
        $("form").submit();
    });
});

// var y = $("body").height() / 2 - $(".search").height();
// $(".searchBox").css("transform", "translate(0px," + y + "px)");
// $(".searchBox").css("transition", "all 0s ease-in-out");

setOptionTopCompanies()
