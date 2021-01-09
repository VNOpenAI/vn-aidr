$(function () {

$("#gen-report-btn").click(function() {

    var doc = new jsPDF()

    doc.setFontSize(40)
    doc.text(15, 25, 'Medical Report')

    doc.setFontSize(12)
    doc.text(15, 40, 'Patient ID:')
    doc.text(15, 45, doc.splitTextToSize("Conclusion: Xin chào anh em", 180))

    let img = new Image()
    img.src = $("#display-image").attr("src");
    doc.addImage(img, 'png', 15, 55, 100, 150)

    doc.save('medical-report.pdf')
});

});