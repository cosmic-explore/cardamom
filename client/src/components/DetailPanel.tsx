import { Card } from '@radix-ui/themes'
import { PositionData } from '../DataTypes'
import { CreatureIcon } from './CreatureSprite'

// type DetailPanelProps {
//     posData: PositionData
// }

export function DetailPanel(props: PositionData) {
    const creature = props.creature

    return (
        <Card className="border p-5">
            {creature ? (
                <div>
                    <div className="flex">
                        <div>
                            <CreatureIcon {...{ speciesName: creature.species_id }} />
                        </div>
                        <div>
                            {creature.nickname} - {creature.species_id}
                        </div>
                    </div>
                    <div>Level: {creature.level}</div>
                    <div>
                        HP: {creature.current_hp}/{creature.max_hp}
                    </div>
                    <div>Speed: {creature.speed}</div>
                </div>
            ) : (
                ''
            )}
        </Card>
    )
}
