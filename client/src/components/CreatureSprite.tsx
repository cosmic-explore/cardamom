import { SpriteMap } from '../constants/sprite-map'

export function CreatureIcon(props: { speciesName: string }) {
    const src = SpriteMap.get(props.speciesName)
    return <img src={src} />
}
