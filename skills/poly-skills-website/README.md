# Crypto Skills

A static Astro directory for browsing crypto-related AI skills by exchange, protocol, and source repository.

## Development

```bash
npm install
npm run dev
```

The catalog is generated from `data.json` files under the parent `skills/` directory:

```bash
npm run build
```

## GitHub Pages

This repo deploys through GitHub Actions to:

```text
https://vinzeny.github.io/crypto-skills/
```

On GitHub, open `Settings` -> `Pages`, then set `Build and deployment` -> `Source` to `GitHub Actions`.

## License

MIT
