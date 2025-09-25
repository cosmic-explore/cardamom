import { SpriteMap } from '../constants/sprite-map'

export function CreatureIcon(props: { speciesName: string }) {
    return <img src={SpriteMap.get(props.speciesName)} />
}
