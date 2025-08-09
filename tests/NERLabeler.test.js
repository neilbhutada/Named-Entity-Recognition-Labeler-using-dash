import React from 'react';
import {render, fireEvent} from '@testing-library/react';
import '@testing-library/jest-dom';
import NERLabeler from '../src/lib/components/NERLabeler.react';

test('double clicking an entity removes it', () => {
  const setProps = jest.fn();
  const entity = {id:1, text:'John', label:'PERSON', start:0, end:4};
  const {getByText} = render(<NERLabeler text="John went home" entities={[entity]} setProps={setProps} />);
  const node = getByText('John');
  fireEvent.doubleClick(node);
  expect(setProps).toHaveBeenCalledWith({entities: []});
});
