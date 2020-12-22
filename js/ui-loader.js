$(function () {

    'use strict';

    var viewer;

    $.get("ui-config.json", function (data) {

        window.UI = {};
        var UI = window.UI;

        // Update document attributes
        document.title = data["title"];
        $(".sidebar-brand-text").html(data["sidebar-brand-text"]);
        $(".sidebar-brand-icon img").attr("src", data["logo"]);

        // Load pages
        let section_menu_html = "";
        let sections = data["sections"];
        UI.sections = sections;

        function selectSection(section_id) {
            
            $("#section-menu li").removeClass("active");
            for (let i = 0; i < window.UI.sections.length; ++i) {
                let section = window.UI.sections[i];
                if (section["id"] == section_id) {
                    console.log("Select: " + section_id);
                    $('#section-menu li[name="'+ section_id +'"]').addClass("active");
                    $("#display-image").attr("src", section["img_placeholder"]);
                    $("#display-image").hide();
                    viewer.update();
                    viewer.moveTo(0, 0);
                    break;
                }
            } 
        }

        // Draw menu
        for (let i = 0; i < sections.length; ++i) {
            section_menu_html += '<li name="'+ sections[i]["id"] +'" class="nav-item">'
                        + '<a class="nav-link" href="#">'
                        + '<i class="fas '+ sections[i]["icon"] +'"></i>'
                        + '<span>'+ sections[i]["title"] +'</span></a></li>';            
        }
        $("#section-menu").html(section_menu_html);
        $("#section-menu li").each(function() {
            $(this).click(function() {
                selectSection($(this).attr("name"));
            });
        });

        
    });

    // View an image
    viewer = new Viewer(document.getElementById('display-image'), {
        inline: true,
        navbar: false,
    });
    viewer.show();

});