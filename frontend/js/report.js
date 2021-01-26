$(function () {

// Add accent when clicking button
$("#add-accent-btn").click(function() {

    let medicalConclusion = $("#medical-conclusion-inp").val();

    $.ajax({
        url: "/api/vn_accent",
        type: 'get',
        data: {"text": medicalConclusion},
        success: function (response) {
            if (response["success"]) {
                $("#medical-conclusion-inp").val(response["with_accent"]);
            } else {
                alert('Error on processing! Please try again.');
            }
        }
    });

});


$("#gen-pdf-btn").click(function() {

    let patientName = $("#patient-name-inp").val();
    let medicalConclusion = $("#medical-conclusion-inp").val();
    let doc = new jsPDF()

    doc.setFont('Arial');
    doc.setFontSize(40)
    doc.text(15, 25, 'Medical Report')

    doc.setFontSize(12)
    doc.text(15, 40, 'Patient Name: ' + patientName)
    doc.text(15, 50, doc.splitTextToSize("Conclusion: " + medicalConclusion, 180))


    doc.save('medical-report.pdf')
});


$("#gen-report-btn").click(function() {
    $("#patient-name-inp").val("");
    $("#medical-conclusion-inp").val("");

    let reportModal = $('#medical-report-modal').modal();
    reportModal.show();
});

});