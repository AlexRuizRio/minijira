Feature: Crear proyecto

  Scenario: Crear un proyecto correctamente
    Given abro el navegador
    And voy a la url "http://127.0.0.1:5000/login"
    When escribo "admin" en el campo "username"
    And escribo "admin123" en el campo "password"
    And pulso ENTER en el campo "password"

    And voy a la url "http://127.0.0.1:5000/proyectos/proyecto/nuevo"

    When escribo "Proyecto QA Auto" en el campo "nombre"
    And escribo "Proyecto creado automáticamente" en el campo "descripcion"
    When pulso el botón "Crear"

    Then deberia ver el mensaje "Proyecto QA Auto"
    And cierro el navegador mostrando "OK"
