Feature: Validaciones de productos

Scenario: Cada producto muestra un precio
    Given abro el navegador
    And voy a la url "https://www.demoblaze.com/"
    Then cada producto debe mostrar un precio
