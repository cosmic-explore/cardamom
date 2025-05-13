import { SpriteMap } from '../constants/sprite-map';

export function CreatureIcon(props: { speciesName: string }) {
    // TODO: pass the species name for real
    let speciesName = 'Test Creature';
    const src = SpriteMap.get(speciesName);

    return <img src={src} />;
}
