import { SpriteMap } from "../constants/sprite-map"
import { PositionData } from "../DataTypes"

export function Position(props: PositionData) {
    const handleClick = () => {
        console.log(props.creature)
    }
    
    return (
        <div className='bg-orange-100 size-12 outline hover:bg-sky-100 flex justify-center items-center' onClick={handleClick}>
            {
                props.creature ? 
                <CreatureIcon {...{speciesName: props.creature.nickname}}/> :
                `${props.x},${props.y}`
            }
        </div>
    )
}

const CreatureIcon = (props: {speciesName: string}) => {
     // TODO: pass the species name for real
    let speciesName = 'Test Creature'
    const src = SpriteMap.get(speciesName)

    return (
        <img src={src}/>
    )
}