import { Card } from '@radix-ui/themes'
import { CreatureState, PositionData } from '../DataTypes'
import { GameSprite } from './GameSprite'

export function DetailPanel(props: {
    creatureState: CreatureState | null
    position: PositionData
}) {
    return (
        <Card className="border p-5">
            <div>Coordinates: {`[${props.position.x},${props.position.y}]`}</div>
            {props.creatureState ? (
                <div>
                    <div className="flex">
                        <div>
                            <GameSprite
                                {...{ spriteName: props.creatureState.creature.species.name }}
                            />
                        </div>
                        <div>
                            {props.creatureState.creature.nickname} -{' '}
                            {props.creatureState.creature.species.name}
                        </div>
                    </div>
                    <div>Level: {props.creatureState.creature.level}</div>
                    <div>
                        HP: {props.creatureState.current_hp}/{props.creatureState.creature.max_hp}
                    </div>
                    <div>Speed: {props.creatureState.creature.speed}</div>
                </div>
            ) : (
                ''
            )}
        </Card>
    )
}
