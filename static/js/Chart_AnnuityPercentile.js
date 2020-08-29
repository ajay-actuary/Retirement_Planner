// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

function number_format(number, decimals, dec_point, thousands_sep) {
  // *     example: number_format(1234.56, 2, ',', ' ');
  // *     return: '1 234,56'
  number = (number + '').replace(',', '').replace(' ', '');
  var n = !isFinite(+number) ? 0 : +number,
    prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
    sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
    dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
    s = '',
    toFixedFix = function(n, prec) {
      var k = Math.pow(10, prec);
      return '' + Math.round(n * k) / k;
    };
  // Fix for IE parseFloat(0.55).toFixed(0) = 0;
  s = (prec ? toFixedFix(n, prec) : '' + Math.round(n)).split('.');
  if (s[0].length > 3) {
    s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
  }
  if ((s[1] || '').length < prec) {
    s[1] = s[1] || '';
    s[1] += new Array(prec - s[1].length + 1).join('0');
  }
  return s.join(dec);
}

var ctx1 = document.getElementById("Chart_AnnuityPercentile");
var Chart_AnnuityPercentile = new Chart(ctx1, {
    type: 'horizontalBar',
    data: {
      labels: ["5", "15", "25", "35", "45", "55", "65", "75", "85", "95"],
      datasets: [
        {
          label: "Expected Annuity (Rs.)",
            borderWidth: 2,
            backgroundColor:  ['#F6C23E','#F6C23E','#F6C23E','#4E73DF','#4E73DF','#4E73DF','#4E73DF','#36B9CC','#36B9CC','#36B9CC'],
          data: []
        }
      ]
    },
    options: {
      legend: { display: false },
      title: {
        display: true,
        text: 'Expected Monthly Annuity by Percentile'
      },
            maintainAspectRatio: false,
    layout: {
      padding: {
        left: 10,
        right: 25,
        top: 25,
        bottom: 0
      }
    },
    scales: {
      xAxes: [{
      scaleLabel: {
        display: true,
        labelString: 'Percentile'
      },
        gridLines: {
          display: false,
          drawBorder: false
        },
      }],
      yAxes: [{
      scaleLabel: {
        display: true,
        labelString: 'Monthly Annuity at Retirement'
      },
        gridLines: {
          color: "rgb(234, 236, 244)",
          zeroLineColor: "rgb(234, 236, 244)",
          drawBorder: false,
          borderDash: [2],
          zeroLineBorderDash: [2]
        }
      }],
    },

    }
});
