$(function () {

    'use strict';

    var viewer;

    function showLoading() {
        $(".loading-modal").show();
    }

    function hideLoading() {
        $(".loading-modal").hide();
    }

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

        function selectFeature(section_id) {
            $("#section-menu li").removeClass("active");
            for (let i = 0; i < window.UI.sections.length; ++i) {
                let section = window.UI.sections[i];
                if (section["id"] == section_id) {
                    console.log("Select: " + section_id);
                    $('#section-title').html(section["title"]);
                    $('#section-menu li[name="' + section_id + '"]').addClass("active");
                    $("#display-image").attr("src", section["img_placeholder"]);
                    $("#display-image").hide();
                    $("#output-log").val('');
                    window.UI.api_endpoint = section["api_endpoint"];
                    viewer.update();
                    viewer.moveTo(0, 0);
                    break;
                }
            }
        }

        // Draw menu
        for (let i = 0; i < sections.length; ++i) {
            section_menu_html += '<li name="' + sections[i]["id"] + '" class="nav-item">' +
                '<a class="nav-link" href="#">' +
                '<i class="fas ' + sections[i]["icon"] + '"></i>' +
                '<span>' + sections[i]["title"] + '</span></a></li>';
        }
        $("#section-menu").html(section_menu_html);
        $("#section-menu li").each(function () {
            $(this).click(function () {
                selectFeature($(this).attr("name"));
            });
        });
        $("#section-menu li").first().click();


    });

    // View an image
    viewer = new Viewer(document.getElementById('display-image'), {
        inline: true,
        navbar: false,
        viewed() {
            viewer.zoomTo(1);
        },
    });
    viewer.show();

    $("#upload-btn").click(function () {
        $('#upload-file').click();
    });
    $('#upload-file').change(function () {

        showLoading();

        var fd = new FormData();
        var files = $(this)[0].files;

        // Check file selected or not
        if (files.length > 0) {
            fd.append('file', files[0]);
            console.log("Sending request to: " + window.UI.api_endpoint);
            $.ajax({
                url: window.UI.api_endpoint,
                type: 'post',
                data: fd,
                contentType: false,
                processData: false,
                success: function (response) {

                    if (response["success"]) {
                        $("#display-image").attr("src", response["image"]);
                        viewer.update();
                        viewer.moveTo(0, 0);
                    } else {
                        alert('Error on processing! Please try again.');
                    }
                    hideLoading();

                    response["image"] = "...";
                    $("#output-log").val(JSON.stringify(response));
                },
                error: function () {
                    hideLoading();
                }
            });
            $(this).val('');
        } else {
            alert("Please select a file.");
        }
    });

});