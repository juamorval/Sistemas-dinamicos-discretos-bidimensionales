// Funciones

function main() {
  extraer_valores();
  añadir_parametros();
  plot_orbita();
  plot_atractor();
 
  $('#orb_tab').on('shown.bs.tab', function () {
    plot_orbita();
  })
  $('#att_tab').on('shown.bs.tab', function () {
    plot_atractor();
  })
  window.addEventListener('resize', function () {
    plot_orbita();
    plot_atractor();
  })
  $(document).ready(function () {
    $('[data-toggle="tooltip"]').tooltip();
  });
  document.getElementById("eq").onkeyup(añadir_parametros())
  $("#go_button").click(function () {
    extraer_valores();
    plot_orbita();
    plot_atractor();

    var _input = document.getElementById("eq").value;
    
    var _iterations = parseFloat(document.getElementById("n").value);
    var _iterations_finals = parseFloat(document.getElementById("m").value);
    var _x0 = parseFloat(document.getElementById("x0").value);
    var _y0 = parseFloat(document.getElementById("y0").value);
    var _values = JSON.stringify(values)

    $.ajax({
      url: "/dinamica",
      type: "get",
      data: { input: _input,  values: _values, n: _iterations, m: _iterations_finals, x0: _x0, y0: _y0 },
      success: function (response) {
        $("#dinamica").html(response);
        $(document).ready(function () {
          $('[data-toggle="tooltip"]').tooltip();
        });
      },
      error: function (xhr) {
        console.log("Hubo un error :/")
        console.log(xhr)
      }
    });
  });

}

function extraer_valores() {
  try {
    stored_equation = document.getElementById("eq").value.split(",");
     
    expr0 = math.parse(stored_equation[0])
    expr1 = math.parse(stored_equation[1])
    iterations = parseFloat(document.getElementById("n").value);
    iterations_finals = parseFloat(document.getElementById("m").value);
    values["x"] = parseFloat(document.getElementById("x0").value);
    values["y"] = parseFloat(document.getElementById("y0").value);
    go_button = document.getElementById("go_button");
  } catch (err) { }
}

function añadir_parametros() {
  let stock = "xXyY";
  var params = new Set();
  values = {}
  values["x"] = parseFloat(document.getElementById("x0").value);
  values["y"] = parseFloat(document.getElementById("y0").value);

  try {
    stored_equation = document.getElementById('eq').value.split(",");
    try {
      expr0 = math.parse(stored_equation[0])
      expr0.traverse(function (node, path, parent) {

        switch (node.type) {
          case 'SymbolNode':
            if (!stock.includes(node.name) && path != 'fn') {
              params.add(node.name);
              values[node.name] = 0
            }
            break
          default:
            break;
        }
      })
    } catch (err) { }

    try {
      expr1 = math.parse(stored_equation[1])
      expr1.traverse(function (node, path, parent) {
        switch (node.type) {
          case 'SymbolNode':
            if (!stock.includes(node.name) && path != 'fn') {
              params.add(node.name);
              values[node.name] = 0
            }
            break
          default:
            console.log(node.type);
            break;
        }
      })
    } catch (err) { }

    var params_html = ""
    params.forEach(function (param) {
      params_html += `<div class="row p-2">
                  <label class="col-md" for="${param}">${param}</label>
                  <input class="col-sm-4" style="text-align: right" type="number" onchange="values[this.id]=parseFloat(this.value)" id="${param}" name="${param}" value="0.0" />
                  </div>`
    })
    document.getElementById("params").innerHTML = params_html

  } catch (err) {
    document.getElementById("params").innerHTML = ""
  }

}

function orbita() {
  var xs = [parseFloat(x0.value)];
  var ys = [parseFloat(y0.value)];

  var itMap = Object.assign({}, values);

  var n = iterations
  var m = iterations_finals

  if(m==0) {
    for (let i = 0; i < n + 1; i++) {
      x_cal = expr0.evaluate(itMap);
      y_cal = expr1.evaluate(itMap);
      itMap["x"] = x_cal;
      itMap["y"] = y_cal;
      xs.push(x_cal);
      ys.push(y_cal);
  
    }
  } else if(m>0) {
    m += n;
    for (let i = 0; i < m + 1; i++) {
      x_cal = expr0.evaluate(itMap);
      y_cal = expr1.evaluate(itMap);
      itMap["x"] = x_cal;
      itMap["y"] = y_cal;
      xs.push(x_cal);
      ys.push(y_cal);
  
    }
  }
  
  

  return [xs, ys];
}



function plot_orbita() {
  orbit = orbita()
  const trace1 = {
    x: orbit[0],
    y: orbit[1],
    type: 'scatter'
  };

  const layout = {
    title: 'Representación de la órbita',
    xaxis: {
      title: 'X'
    },
    yaxis: {
      title: 'Y',
    }
  };


  const data = [trace1];
  Plotly.newPlot("plot_orb", data, layout);
}

function plot_atractor() {
  orbit=orbita()
  const trace1 = {
    x: orbit[0],
    y: orbit[1],
    mode: 'markers',
    marker: { size: 5 }
  };

  const layout = {
    title: 'Representación de los atractores',
    xaxis: {
      title: 'X'
    },
    yaxis: {
      title: 'Y'
    }
  };

  const data = [trace1];
  Plotly.newPlot("plot_att", data, layout);

}

