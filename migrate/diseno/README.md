> **Documento histórico.** Registra la elección de tema de fines de agosto /
> principios de septiembre de 2026, cuando las cuatro opciones se probaban sobre
> un demo. El sitio quedó con la **D**, y las capas SCSS ya no están acá sino en
> `assets/` de la raíz, donde siguieron cambiando. Dos cosas que dice más abajo
> ya no valen: el sitio **no tiene página About** (la bio está en el hero del
> home), y el hero usa `image-shape: rounded`, no `round`, que sobre una imagen
> no cuadrada da una elipse. Lo que sí sigue vigente son las decisiones de
> paleta y las razones de contraste del final.

# Tres opciones de tema — paleta andreo-theme.scss

Vista previa comparada: ver el artifact "Tres identidades Andreo".

Cada opción son 3 capas: base (paleta + tipografías) + la opción + reglas comunes.
En `_quarto.yml`:

```yaml
format:
  html:
    theme:
      - cosmo
      - assets/_andreo-base.scss
      - assets/andreo-a-navbar-navy.scss      # ← cambiar por la b o la c
      - assets/_andreo-comun.scss
```

| Archivo | Opción |
|---|---|
| `andreo-a-navbar-navy.scss` | A — navbar y footer navy sólidos, tarjetas con sombra, teal de marca |
| `andreo-b-editorial-clara.scss` | B — navbar paper con filete y subrayado teal, títulos serif navy, tarjetas con borde |
| `andreo-c-banda-navy.scss` | C — banda navy en el hero, eyebrows ocre, año en chip oro, código sobre navy |
| `andreo-d-navy-hero-split.scss` | **D — la A con el hero partido de la B** (foto grande a la izquierda, nombre y datos a la derecha) |

La C además necesita en el `index.qmd` del home:

```yaml
title-block-banner: "#0E2A3D"
```

La D usa el bloque `about` del home con `solana` y la fila invertida por CSS
(el `row-reverse` ya está en el scss). `trestles` no sirve para ese hero: apila
el nombre debajo de la foto en vez de ponerlo al lado.

```yaml
about:
  template: solana
  image-width: 14em
  image-shape: round
```

La página About sí usa `trestles`, que ahí es lo correcto.

El contenido del header de la B, la C y la D es el mismo — en el cuerpo del `index.qmd`:

```markdown
[Researcher & Lecturer]{.eyebrow}

# Verónica Andreo

Remote sensing · vector-borne disease ecology · GRASS GIS

[Instituto Gulich](http://ig.conae.unc.edu.ar/) · [CONICET](https://www.conicet.gov.ar/) · Córdoba, Argentina
```

Las cuatro compilan con Quarto 1.7.31 sobre el demo de `../migrate-hugo/veroandreo-quarto-demo`.

## Contraste

- teal `#1F7A6C` sobre paper `#FBFAF6` → 5.0:1, cumple AA para texto normal → es el color de links en las cuatro.
- ocre `#C97A2E` sobre paper → 3.2:1, **no** alcanza para texto de párrafo; queda para títulos, chips y filetes.
- oro `#F6C453` sobre navy → 9:1; solo se usa sobre navy.
