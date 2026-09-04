# Sitio de Verónica Andreo - guía de uso

Sitio en Quarto. Esta guía es para el día a día: dónde tocar cada cosa.
El registro de la migración desde Hugo está en `migrate/MIGRACION.md`, una
carpeta **local, no versionada** (ver Estructura).

---

## Trabajar con el sitio

```bash
quarto preview      # servidor local con recarga automática
quarto render       # genera _site/ completo
quarto render index.qmd    # una sola página, más rápido
```

Requiere Quarto 1.7+ y, para los scripts de `migrate/` (local, no versionada),
Python 3.11+ con PyYAML.

`_site/` y `.quarto/` son productos de compilación: están en `.gitignore` y no se
versionan. Si algo se ve raro después de un cambio de estilos, `rm -rf _site .quarto`
y volver a renderizar.

---

## Estructura

```
_quarto.yml           configuración del sitio: navbar, footer, tema, favicon, recursos
index.qmd             home: hero con la bio, Interests, Skills, publicaciones,
                      Experience y Contact
publications/         una carpeta por publicación, cada una con su index.qmd
posts/                idem posts
talks/                idem charlas y talleres
courses/index.qmd     página de cursos (una lista a mano, sin listing)
assets/
  ├── _andreo-base.scss              paleta y tipografías
  ├── andreo-d-navy-hero-split.scss  la opción de diseño en uso
  ├── andreo-a/b/c-*.scss            las otras tres opciones
  ├── _andreo-comun.scss             estilos compartidos por las cuatro
  ├── img/                           avatar, caricatura, favicon, headers, logos
  └── cv.pdf
migrate/              scripts de migración y mantenimiento, y `about-old.qmd`
                      - local, no versionada
```

**`migrate/` no está en el repo.** Está en el `.gitignore`, así que vive sólo en
la copia local: los scripts de mantenimiento, el registro de la migración
(`MIGRACION.md`), el de diseño (`diseno/`) y `about-old.qmd`. Los comandos de
este README que la nombran funcionan en local; en un clon nuevo hay que copiarla
a mano. También está excluida del render en `_quarto.yml`
(`render: - "!migrate/"`), que no se queja si la carpeta no existe.

**No hay página About.** La bio vive en el hero del home, como estaba en Hugo. La
página vieja quedó guardada, sin renderizar, en `migrate/about-old.qmd`: ahí están
también Education y la versión anterior de Interests, por si alguna vez vuelven.

---

## Dónde está cada estilo

Casi todo vive en dos archivos. Regla práctica: **si se ve igual en las cuatro
opciones de diseño, está en `_andreo-comun.scss`; si es propio de esta opción,
está en `andreo-d-navy-hero-split.scss`**.

| Quiero cambiar… | Archivo | Buscar |
|---|---|---|
| Colores de la paleta | `assets/_andreo-base.scss` | `// Primarios` |
| Tipografías | `assets/_andreo-base.scss` | `// Tipografías` |
| Navbar (colores, hover) | `andreo-d-navy-hero-split.scss` | `.navbar-nav .nav-link` |
| Hero del home (las dos columnas) | `andreo-d-navy-hero-split.scss` | `.hero-split` |
| Cargo y afiliación del hero | `andreo-d-navy-hero-split.scss` | `.hero-role` |
| Botones sociales redondos | `andreo-d-navy-hero-split.scss` | `.hero-links .about-link` |
| Iconos del footer | `andreo-d-navy-hero-split.scss` | `.footer-icon` |
| Tarjetas: orden y estilo | `_andreo-comun.scss` | `── Tarjetas` |
| Tags / categorías | `_andreo-comun.scss` | `listing-category` |
| Chip del año | `_andreo-comun.scss` | `.listing-date` |
| Grilla de Skills | `_andreo-comun.scss` | `── Skills` |
| Grupos de Interests | `_andreo-comun.scss` | `── Interests` |
| Timeline de Experience | `_andreo-comun.scss` | `── Experience` |
| Bloque de contacto y mapa | `_andreo-comun.scss` | `── Contacto` / `── Mapa` |
| Tamaño de la figura de cada publicación | `_andreo-comun.scss` | `── La figura destacada` |
| Espacio entre secciones | `_andreo-comun.scss` | `── Aire entre secciones` |
| Navbar fija al hacer scroll | `_andreo-comun.scss` | `── Navbar siempre a la vista` |
| Callouts | `_andreo-comun.scss` | `── Iconos de los callouts` |

### Cambiar los colores

En `assets/_andreo-base.scss`:

```scss
$navy:   #0E2A3D;  // navbar, footer, chips de categoría
$teal:   #1F7A6C;  // acento: links, iconos, chip del año
$ochre:  #C97A2E;  // acento secundario: rótulos de sección, hover de links
$gold:   #F6C453;  // hover del menú y del footer, solo sobre navy
$ink:    #16211A;  // texto
$muted:  #5C6670;  // texto secundario
$paper:  #FBFAF6;  // fondo
$rule:   #DCD8CA;  // filetes y bordes
```

Cambiar uno de estos se propaga a todo el sitio. **Contraste**: el teal sobre
paper da 5.0:1 y cumple AA para texto; el ocre da 3.2:1, así que sirve para
rótulos, chips y filetes pero **no para texto de párrafo**; el oro solo funciona
sobre navy (9:1).

### Cambiar de opción de diseño

En `_quarto.yml`, la línea del medio del bloque `theme:`:

```yaml
theme:
  - cosmo
  - assets/_andreo-base.scss
  - assets/andreo-d-navy-hero-split.scss   # ← cambiar por a, b o c
  - assets/_andreo-comun.scss
```

Las opciones A y C piden además un ajuste en `index.qmd` (para la C,
`title-block-banner`). Está anotado en el encabezado de cada `.scss`.

**Ojo**: las reglas del hero (`.hero-split` y compañía) viven **sólo** en el
archivo D. A, B y C se escribieron cuando el hero salía del bloque `about:` de
Quarto, así que si hoy cambiás de opción hay que llevarse esas reglas al archivo
elegido, o el hero queda sin estilo.

**Orden y precedencia**: Quarto compila los archivos en orden. En `scss:defaults`
gana **el último** de la lista; en `scss:rules` también gana el último, pero
**solo a igual especificidad**. Por eso `_andreo-comun.scss` va al final.

---

## Contenido

### Agregar una publicación

Crear `publications/<slug>/index.qmd`. Front matter mínimo:

```yaml
---
title: "Título del paper"
date: '2026-03-15'          # YYYY-MM-DD; en las tarjetas se muestra solo el año
author:
  - name: V. Andreo
  - name: J. Pérez
doi: 10.1000/ejemplo
categories:
  - Remote sensing
  - Dengue
image: featured.jpg          # opcional; si no está, va el placeholder
---

[PDF](https://doi.org/…) · [Code](…)

## Abstract

…

![](featured.jpg){fig-alt="…" .featured-figure}

## Citation

…
```

El slug de la carpeta es la URL. Las categorías tienen que salir del vocabulario
(ver abajo), y los nombres de especie van en itálica con `*Aedes aegypti*`, tanto
en el título como en el cuerpo.

Posts y charlas son igual, en `posts/` y `talks/`. Las charlas además usan
`event`, `event_url`, `location` y `when`.

### Cuántas publicaciones o posts se muestran

| Dónde | Archivo | Clave |
|---|---|---|
| Home, publicaciones recientes | `index.qmd` | `max-items: 6` y `grid-columns: 3` |
| Página Publications | `publications/index.qmd` | `page-size: 24` (paginado) |
| Página Posts | `posts/index.qmd` | `type: default` (filas, sin límite) |
| Página Talks | `talks/index.qmd` | `type: grid`, `grid-columns: 3` |

`max-items` × `grid-columns` define las filas: 6 y 3 son dos filas de tres.

Otras claves útiles de los listados: `sort: "date desc"`, `date-format: "YYYY"`
(solo el año), `categories: true` (barra lateral de categorías), `filter-ui` y
`sort-ui` (buscador y selector de orden), `image-height`, `image-placeholder`,
`fields:` (qué se muestra en cada tarjeta).

### Agregar o quitar una sección del home

Las secciones son `##` con la clase del rótulo:

```markdown
## Recent publications {.section-label}
```

Para un listado hacen falta **dos cosas**: la declaración en el front matter
(`listing: - id: latest-publications …`) y el div donde va (`::: {#latest-publications} :::`).

> **Ojo:** si borrás el div pero dejás la declaración, Quarto renderiza el
> listado igual y lo cuelga **al final de la página**. Para sacar una sección hay
> que borrar las dos partes.

El link "ver todo" al pie de un listado va alineado a la derecha envolviéndolo:

```markdown
::: {.more-link}
[All publications →](publications/index.qmd)
:::
```

### El hero del home

Está escrito **a mano** en `index.qmd`, sin el bloque `about:` de Quarto. Son dos
columnas:

```
[ foto   ]  RESEARCHER & LECTURER
[ iconos ]  Verónica Andreo
            CONICET · INSTITUTO GULICH - CONAE/UNC
            bio…
```

````markdown
::: {#hero .hero-split}

::: {.hero-side}
```{=html}
<img src="assets/img/caricatura-web.jpg" class="hero-photo" alt="…">
```

::: {.hero-links}
[{{< ai orcid >}}](https://orcid.org/…){.about-link aria-label="ORCID"}
…
:::
:::

::: {.hero-main}
::: {.hero-role}
Researcher & Lecturer
:::

```{=html}
<h1 class="hero-name">Verónica Andreo</h1>
```

::: {.hero-affiliation}
[CONICET](…) · [Instituto Gulich](…) - [CONAE](…)/[UNC](…)
:::

My research asks a simple question with a difficult answer: …
:::

:::
````

Para editar el texto de la bio, los párrafos de `.hero-main`. Para sumar o sacar
un ícono, una línea en `.hero-links`: es un link markdown común con la clase
`.about-link`, que es la que le da el círculo teal.

Cuatro cosas que conviene saber antes de tocarlo:

- **Por qué no usa `about:`.** En el template `solana` los iconos y el cargo
  salen dentro de la columna del texto y no hay CSS que los pase a la de la
  foto: con grid no se puede porque las filas son comunes a las dos columnas, y
  la bio terminaría arrancando debajo de la foto. `trestles` tampoco sirve:
  llevaría también el nombre a la columna de la foto.
- **`body-classes: home-hero`** en el front matter no es decorativo: activa la
  regla que esconde el title block de Quarto. Si se saca, aparece un segundo
  nombre arriba de todo. El `title:` se mantiene porque de ahí salen el
  `<title>` y las tarjetas de redes; el `<h1>` que se ve es el del hero.
- **La foto y el nombre van en bloques ```` ```{=html} ````** para que no queden
  envueltos en un `<p>`. Una imagen sola en un párrafo markdown se convierte
  además en un `<figure>` con epígrafe.
- **En móvil** las dos columnas se aplanan con `display: contents` y cada
  elemento se reordena por separado: foto → cargo → nombre → afiliación →
  iconos → bio. Por eso el `order` del media query va elemento por elemento y no
  por columna.

---

## Imágenes

- **De cada publicación**: `featured.jpg` o `.png` dentro de su carpeta.
  Conviene redimensionar a ~1400 px de ancho antes de subirlas.
- **Placeholder** de las que no tienen: `assets/img/headers/landsatlooks.jpg`,
  configurado en `image-placeholder` de cada listado.
- **Tamaño en la página**: 65 % del ancho del texto, centrada. Se cambia en un
  solo lugar, `_andreo-comun.scss` → `img.featured-figure { max-width: 65% }`.
  Para una figura puntual se puede pisar desde el `.qmd` con `{width=40%}`.
- **Logos de instituciones**: `assets/img/logos/`.
- **Retratos**: `assets/img/caricatura-web.jpg` (768 px, 247 KB) es la del hero;
  el original `caricatura.png` pesa 2,8 MB y no se sirve. `avatar.jpg` sigue
  siendo el `image:` de la página, que es lo que usan las tarjetas de redes
  sociales — ahí conviene una imagen cuadrada.
- **Favicon**: `assets/img/favicon.png` (192 px, redimensionado del mismo archivo
  que usaba Hugo), declarado en `_quarto.yml` con `favicon:`. Quarto reescribe la ruta según la profundidad
  de cada página.

Quarto solo copia al sitio las imágenes que alguna página referencia. Las que se
usan como placeholder no cuentan, por eso están declaradas en `resources:` de
`_quarto.yml`.

---

## Iconos

Hay dos juegos cargados:

- **Font Awesome 6.7.2**, para todo lo general: `<i class="fa-solid fa-brain"></i>`
  o, en markdown, `[]{.fa-solid .fa-brain}`.
- **academicons**, para lo académico: `{{< ai orcid >}}`, `{{< ai overleaf >}}`,
  `{{< ai google-scholar >}}`. La lista completa está en
  `_extensions/schochastics/academicons/assets/css/all.css`.

El shortcode también funciona como texto de un link, que es como están puestos
los iconos del hero: `[{{< ai orcid >}}](https://orcid.org/…){.about-link}`.

---

## Mantenimiento

### Categorías

El vocabulario está en `migrate/mapa_categorias.py` (carpeta local, no
versionada): un diccionario de `etiqueta actual → canónica` y un conjunto
`BORRAR` con las que se eliminan.

```bash
python3 migrate/aplicar_categorias.py --dry-run   # simula y muestra el resultado
python3 migrate/aplicar_categorias.py             # escribe los .qmd
```

Para fusionar dos categorías, agregar la línea al mapa y volver a correrlo. El
script relee los archivos cada vez, así que no importa si editaste a mano.

### Itálicas de nombres científicos

```bash
python3 migrate/italicas_especies.py --dry-run
python3 migrate/italicas_especies.py
```

Para sumar una especie, agregarla a `BINOMIALES` o `GENEROS` dentro del script.
No toca bloques de código, URLs ni lo que ya estaba en itálica, y es seguro
correrlo dos veces.

---

## Publicar

El sitio está en <https://veroandreo.github.io>. Para publicar un cambio:

```bash
git add -A && git commit -m "..." && git push
```

Y listo. El workflow `.github/workflows/publish.yml` renderiza con Quarto 1.7.31
y empuja el HTML a la rama `gh-pages`, que es la que sirve GitHub Pages. Tarda
alrededor de un minuto. Para seguirlo: `gh run watch`.

**No hace falta renderizar antes de pushear**, ni commitear `_site/`: lo hace el
workflow. Renderizá local sólo para mirar el resultado antes de subirlo.

Si actualizás Quarto en tu máquina, subí también la versión del workflow (línea
`version:`) para que local y CI no se separen.

La rama `gh-pages` la maneja el workflow: no se toca a mano.

---

## Si algo no se ve como esperabas

1. **¿Estás mirando el build actual?** `rm -rf _site .quarto && quarto render`.
   Un `quarto preview` viejo en otra pestaña sirve la versión anterior.
2. **¿La regla CSS está aplicándose o solo existe?** Que aparezca en el CSS
   compilado no significa que gane. Quarto usa selectores muy específicos
   (`div.quarto-about-trestles .about-entity .about-link`, por ejemplo); en el
   inspector, mirá la pestaña Computed y fijate qué regla tacha a cuál.
3. **¿Un CSS de CDN no hace nada?** Revisá que no tenga un `integrity` incorrecto:
   el navegador descarta la hoja entera sin decir nada.
