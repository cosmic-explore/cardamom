import { SpriteMap } from '../constants/sprite-map'

export function GameSprite(props: { spriteName: string }) {
    return <img src={SpriteMap.get(props.spriteName)} />
}
