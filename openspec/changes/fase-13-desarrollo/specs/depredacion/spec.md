# Spec Delta

## ADDED Requirements

### Requirement: Ataque según el tamaño
Con `ataque.tamano`, el daño de cada ataque SHALL multiplicarse por r²/(1+r²), donde r es el tamaño del grupo conexo del atacante dividido por el del atacado (con `ataque.forma = "suave"`, por r/(1+r)). Esta regla MUST reemplazar a la protección por enlaces.

#### Scenario: Iguales y desiguales
- **WHEN** una célula suelta ataca a otra suelta
- **THEN** el daño es la mitad de la fuerza
- **WHEN** un grupo de 3 ataca a una suelta
- **THEN** el daño es 0,9 de la fuerza, y una suelta que ataca a un grupo de 3 hace 0,1

### Requirement: Control sin canibalismo interno
Con `ataque.tamano` y `ataque.intragrupo = false`, los ataques entre miembros de un mismo grupo conexo SHALL no tener efecto. Siempre MUST contarse aparte como ataques dentro del grupo.

#### Scenario: Ataque a un socio
- **WHEN** una célula ataca a un socio de su propio grupo con el control activo
- **THEN** ninguna de las dos cambia su energía, y el ataque se cuenta como dentro del grupo
