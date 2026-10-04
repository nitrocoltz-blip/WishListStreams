# Nitrocolt Wishlist

Página de wishlist para Twitch sincronizada con Steam mediante GitHub Actions y publicada en GitHub Pages (sin dominio propio).

## Puesta en marcha

1. Sube todo el contenido de esta carpeta a un repositorio de GitHub (rama `main`), incluida la carpeta oculta `.github`.
2. En **Settings > Pages**, en *Source* elige **GitHub Actions**.
3. En **Settings > Actions > General > Workflow permissions** marca **Read and write permissions**.
4. En la pestaña **Actions**, abre *Actualizar y publicar wishlist* y pulsa **Run workflow**.
5. Tu web quedará en `https://TU_USUARIO.github.io/NOMBRE_DEL_REPO/`.

A partir de ahí, el workflow se ejecuta cada 6 horas, en cada push y a mano. Lee tu wishlist de Steam, guarda `data/wishlist.json` y vuelve a publicar la web. La página además se refresca sola cada 5 minutos mientras está abierta.

## Requisitos de Steam

Perfil y **detalles de juego** en público (Steam > Perfil > Editar perfil > Privacidad). Si no, Steam devuelve la wishlist vacía.

## Juegos regalados

Steam quita de la wishlist los juegos que ya tienes. Para que sigan saliendo como "Regalado", añádelos en `data/manual.json`:

```json
{ "1326470": { "gifted": true, "giftedBy": "nombre del viewer" } }
```
