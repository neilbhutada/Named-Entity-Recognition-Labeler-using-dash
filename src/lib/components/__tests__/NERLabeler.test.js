import React from 'react';
import {render, fireEvent} from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import NERLabeler from '../NERLabeler.react';

test('double clicking an entity removes it', () => {
  const mockSetProps = jest.fn();
  const entity = {id: 1, text: 'John', label: 'PERSON', start: 0, end: 4};
  const {getByText} = render(
    <NERLabeler text="John went home" entities={[entity]} setProps={mockSetProps} />
  );
  const span = getByText('John');
  fireEvent.doubleClick(span);
  expect(mockSetProps).toHaveBeenCalledWith({entities: []});
});
