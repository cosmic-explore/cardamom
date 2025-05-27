import { Card } from '@radix-ui/themes'
import { CreatureData, PositionData } from '../DataTypes'
import { CreatureIcon } from './CreatureSprite'

export function DetailPanel(props: { creature: CreatureData | null; position: PositionData }) {
    return (
        <Card className="border p-5">
            <div>Coordinates: {`[${props.position.x},${props.position.y}]`}</div>
            {props.creature ? (
                <div>
                    <div className="flex">
                        <div>
                            <CreatureIcon {...{ speciesName: props.creature.species_id }} />
                        </div>
                        <div>
                            {props.creature.nickname} - {props.creature.species_id}
                        </div>
                    </div>
                    <div>Level: {props.creature.level}</div>
                    <div>
                        HP: {props.creature.current_hp}/{props.creature.max_hp}
                    </div>
                    <div>Speed: {props.creature.speed}</div>
                </div>
            ) : (
                ''
            )}
        </Card>
    )
}
