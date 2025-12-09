Feature: Login del sistema

  Scenario: Login válido
    Given abro el navegador
    And voy a la url "http://127.0.0.1:5000/login"
    When escribo "admin" en el campo "username"
    And escribo "admin123" en el campo "password"
    And pulso ENTER en el campo "password"
    Then deberia ver el mensaje "Inicio de sesión exitoso."
    And cierro el navegador mostrando "OK"
